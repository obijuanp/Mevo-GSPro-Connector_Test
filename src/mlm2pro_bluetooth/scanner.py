from bleak import BLEDevice
from bleak import BleakScanner


class MLM2PROScanner:
    MLM2PRO_NAME_PREFIX = "MLM2-"
    BLUEZ_NAME_PREFIX = "BlueZ"

    @classmethod
    async def discover(cls, timeout: float = 5) -> list[BLEDevice]:
        devices = await BleakScanner.discover(timeout=timeout)  # type: ignore
        return [dev for dev in devices if dev.name and (dev.name.startswith(MLM2PROScanner.MLM2PRO_NAME_PREFIX) or dev.name.startswith(MLM2PROScanner.BLUEZ_NAME_PREFIX))]