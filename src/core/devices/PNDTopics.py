import re
from typing import Optional, Tuple


class PNDTopics:
    # Base topics
    ROOT = "plantdoctor"

    # Topic suffixes
    STATUS = "status"
    SENSORS = "sensors"
    ERROR = "error"
    COMMAND = "command"
    POWER = "power"
    DISCOVERY = "discovery"
    CONFIG = "config"
    AVAILABILITY = "availability"

    @classmethod
    def device_topic(cls, device_id: str, suffix: str = "") -> str:
        """
        Returns the full MQTT topic for a given device and suffix.
        Example: device_topic("deviceA", "status") -> "plantdoctor/device/deviceA/status"
        """
        if suffix:
            return f"{cls.ROOT}/device/{device_id}/{suffix}"
        return f"{cls.ROOT}/device/{device_id}"

    @classmethod
    def device_status_topic(cls, device_id: str) -> str:
        """Get device status topic."""
        return cls.device_topic(device_id, cls.STATUS)

    @classmethod
    def device_sensors_topic(cls, device_id: str) -> str:
        """Get device sensors topic."""
        return cls.device_topic(device_id, cls.SENSORS)

    @classmethod
    def device_command_topic(cls, device_id: str) -> str:
        """Get device command topic."""
        return cls.device_topic(device_id, cls.COMMAND)

    @classmethod
    def device_power_topic(cls, device_id: str) -> str:
        """Get device power command topic."""
        return cls.device_topic(device_id, cls.POWER)

    @classmethod
    def device_config_topic(cls, device_id: str) -> str:
        """Get device config topic."""
        return cls.device_topic(device_id, cls.CONFIG)

    @classmethod
    def device_availability_topic(cls, device_id: str) -> str:
        """Get device availability topic (for LWT)."""
        return cls.device_topic(device_id, cls.AVAILABILITY)

    @classmethod
    def discovery_topic(cls) -> str:
        """Get global discovery topic."""
        return f"{cls.ROOT}/{cls.DISCOVERY}"

    @classmethod
    def is_device_topic(cls, topic: str) -> Tuple[bool, Optional[str]]:
        """
        Check if topic is a device topic and extract device ID.
        Returns (is_device_topic, device_id)
        """
        pattern = rf"^{cls.ROOT}/device/([^/]+)(?:/.*)?$"
        match = re.match(pattern, topic)

        if match:
            return True, match.group(1)
        return False, None

    @classmethod
    def extract_device_id(cls, topic: str) -> Optional[str]:
        """Extract device ID from topic if it's a device topic."""
        _, device_id = cls.is_device_topic(topic)
        return device_id
