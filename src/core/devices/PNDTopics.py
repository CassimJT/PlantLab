class PNDTopics:
    ROOT = "pnd"

    STATUS = "status"
    SENSORS = "sensors"
    ERROR = "error"

    COMMAND = "command"
    POWER = "power"

    @staticmethod
    def device_topic(device_id: str, suffix: str) -> str:
        """
        Returns the full MQTT topic for a given device and suffix.
        Example: device_topic("deviceA", PNDTopics.POWER) -> "pnd/deviceA/power"
        """
        return f"{PNDTopics.ROOT}/{device_id}/{suffix}"
