from homeassistant.const import Platform

# Global Constants
DOMAIN: str = "swegon"
PLATFORMS = [Platform.NUMBER, Platform.SELECT, Platform.SENSOR, Platform.SWITCH]

# Configuration Device Constants
CONF_NAME: str = "name"
CONF_IP: str = "ip_address"
CONF_PORT: str = "port"
CONF_SCAN_INTERVAL: str = "scan_interval"

# Defaults
DEFAULT_SCAN_INTERVAL: int = 300  # Seconds
