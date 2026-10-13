from __future__ import annotations

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Any, Callable
from pymodbus.client import AsyncModbusSerialClient, AsyncModbusTcpClient

from .devices.modbustraffic import ModbusTrafficStats

_LOGGER = logging.getLogger(__name__)


# ============================================================================
# Base bus manager
# ============================================================================
class BaseBusManager(ABC):
    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        self._client = None
        self._users: set[str] = set()

        # Traffic statistics
        self.traffic = ModbusTrafficStats()              # bus-level
        self._device_traffic: dict[int, ModbusTrafficStats] = {}

        # Context for packet tracing
        self._active_slave: int | None = None

    # ------------------------------------------------------------------
    # Device registration
    # ------------------------------------------------------------------

    def register_device(self, slave_id: int, stats: ModbusTrafficStats) -> None:
        """Register per-device traffic stats."""
        self._device_traffic[slave_id] = stats

    def unregister_device(self, slave_id: int) -> None:
        self._device_traffic.pop(slave_id, None)

    # ------------------------------------------------------------------
    # Packet tracing (called by pymodbus)
    # ------------------------------------------------------------------
    def _bus_packet_trace(self, is_tx: bool, packet: bytes) -> bytes:
        """Trace packets at both bus and device level."""

        # Bus-level stats
        if is_tx:
            self.traffic.record_tx(len(packet))
        else:
            self.traffic.record_rx(len(packet))

        # Device-level stats (if we know who is active)
        if self._active_slave is not None:
            stats = self._device_traffic.get(self._active_slave)
            if stats:
                if is_tx:
                    stats.record_tx(len(packet))
                else:
                    stats.record_rx(len(packet))

        return packet

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    @abstractmethod
    async def async_start(self) -> None: ...

    @abstractmethod
    async def async_stop(self) -> None: ...

    @property
    def connected(self) -> bool:
        return self._client is not None

    # ------------------------------------------------------------------
    # Reference tracking (Home Assistant config entries)
    # ------------------------------------------------------------------
    def attach(self, entry_id: str) -> None:
        self._users.add(entry_id)

    async def detach(self, entry_id: str) -> bool:
        self._users.discard(entry_id)

        if not self._users:
            await self.async_stop()
            return True

        return False

    # ------------------------------------------------------------------
    # Serialized execution
    # ------------------------------------------------------------------
    async def execute(self, slave_id: int, func: Callable[..., Any], *args, **kwargs) -> Any:
        """Execute a Modbus call with locking and slave context."""
        await self.async_start()

        async with self._lock:
            self._active_slave = slave_id
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                # Record error at bus level
                self.traffic.record_error()
                
                # Record error at device level if known
                if self._active_slave is not None:
                    stats = self._device_traffic.get(self._active_slave)
                    if stats:
                        stats.record_error()

                # Re-raise so the device/coordinator sees the exception
                raise
            finally:
                self._active_slave = None   


# ============================================================================
# RTU bus manager
# ============================================================================
class RTUBusManager(BaseBusManager):
    """Shared Modbus RTU serial bus."""

    def __init__(self, *, port: str, baudrate: int, parity: str='N', stopbits: int=1, timeout: float=3) -> None:
        super().__init__()

        self.port = port
        self._serial_cfg = {"baudrate": baudrate, "parity": parity, "stopbits": stopbits, "timeout": timeout}

    async def async_start(self) -> None:
        if self._client is not None:
            return

        _LOGGER.debug("Opening Modbus RTU bus on %s", self.port)

        client = AsyncModbusSerialClient(port=self.port, **self._serial_cfg, trace_packet=self._bus_packet_trace)

        await client.connect()

        if not client.connected:
            client.close()
            raise ConnectionError(f"Failed to open RTU port {self.port}")

        self._client = client

    async def async_stop(self) -> None:
        if self._client is None:
            return

        _LOGGER.debug("Closing Modbus RTU bus on %s", self.port)
        self._client.close()
        self._client = None

    def matches_serial_config(self, *, baudrate: int, parity: str='N', stopbits: int=1, timeout: float) -> bool:
        return self._serial_cfg == {"baudrate": baudrate, "parity": parity, "stopbits": stopbits, "timeout": timeout}

# ============================================================================
# TCP bus manager
# ============================================================================
class TCPBusManager(BaseBusManager):
    """Shared Modbus TCP connection."""

    def __init__(self, *, host: str, port: int, timeout: float=3) -> None:
        super().__init__()
        self.host = host
        self.port = port
        self.timeout = timeout

    async def async_start(self) -> None:
        if self._client is not None:
            return

        _LOGGER.debug("Opening Modbus TCP bus %s:%s", self.host, self.port)

        client = AsyncModbusTcpClient(host=self.host, port=self.port, timeout=self.timeout, trace_packet=self._bus_packet_trace)

        await client.connect()

        if not client.connected:
            client.close()
            raise ConnectionError(
                f"Failed to connect to Modbus TCP {self.host}:{self.port}"
            )

        self._client = client
        _LOGGER.debug("Created client!")

    async def async_stop(self) -> None:
        if self._client is None:
            return

        _LOGGER.debug("Closing Modbus TCP bus %s:%s", self.host, self.port)
        self._client.close()
        self._client = None

# ============================================================================
# Bus client (one per device)
# ============================================================================
class BusClient:
    """
    Device-facing Modbus client, proxy for pymodbus calls.
    Each BusClient represents exactly ONE slave/device.
    """

    def __init__(self, bus: BaseBusManager, slave_id: int) -> None:
        self._bus = bus
        self.slave_id = slave_id

    async def connect(self) -> None:
        # Optional explicit connect; bus auto-connects anyway
        await self._bus.async_start()

    async def close(self) -> None:
        # Lifecycle is owned by the bus manager
        return

    @property
    def connected(self) -> bool:
        return self._bus.connected

    def __getattr__(self, name: str):
        if name.startswith("_"):
            raise AttributeError(name)

        async def proxy(*args, **kwargs):
            await self._bus.async_start() 
            client = self._bus._client
            if client is None:
                raise ConnectionError("Modbus client not available")

            method = getattr(client, name)
            if not callable(method):
                return method

            return await self._bus.execute(self.slave_id, method, *args, **kwargs)

        return proxy