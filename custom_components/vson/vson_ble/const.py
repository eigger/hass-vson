from sensor_state_data import (
    BaseDeviceClass,
)
SERVICE_WP6003 = "0000fff0-0000-1000-8000-00805f9b34fb"
CHAR_CMD = "0000fff1-0000-1000-8000-00805f9b34fb"
CHAR_NOTI = "0000fff4-0000-1000-8000-00805f9b34fb"

class ExtendedSensorDeviceClass(BaseDeviceClass):
    """Device class for additional sensors (compared to sensor-state-data)."""

    # Data channel
    CHANNEL = "channel"

    # Raw hex data
    RAW = "raw"

    # Text
    TEXT = "text"

    # Volume storage
    VOLUME_STORAGE = "volume_storage"

    # Direction
    DIRECTION = "direction"

    # Precipitation
    PRECIPITATION = "precipitation"

