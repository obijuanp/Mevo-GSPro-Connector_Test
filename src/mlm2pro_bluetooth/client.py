import asyncio
import logging
from typing import Callable

from PySide6.QtCore import QObject, Signal
from bleak import BleakClient, BLEDevice
from bleak.backends.service import BleakGATTService


class MLM2PROClient(QObject):

    mlm_client_connecting = Signal()
    mlm_client_disconnected = Signal()
    mlm_client_disconnecting = Signal()

    def __init__(
        self,
        device: BLEDevice,
        connect_timeout: float = 10
    ) -> None:
        super().__init__()
        self.bleak_client = BleakClient(device, timeout=connect_timeout, disconnected_callback=self.__disconnected)
        self.device = device
        self.connect_timeout = connect_timeout
        self.subscriptions = []
        self.started = False

    async def start(self) -> None:
        print('client start')
        print('connecting')
        self.mlm_client_connecting.emit()
        await self.__connect()
        self.started = True

    async def stop(self) -> None:
        print('client stop')
        self.mlm_client_disconnecting.emit()
        await self.__disconnect()
        self.started = False

    async def __connect(self) -> None:
        if not self.is_connected:
            logging.debug(f'Attempting to connect to device: {self.device.name} {self.device.address}')
            for i in range(3):
                try:
                    print('bleak connect')
                    await self.bleak_client.connect()
                    print('connected')
                    break
                except WindowsError as e:
                    logging.debug(f'Error while connecting WindowsError: {e}')
                    await asyncio.sleep(1)

    async def __disconnect(self) -> None:
        if self.is_connected:
            logging.debug(f'Disconnecting from device: {self.device.name} {self.device.address}')
            #await self.bleak_client.unpair()
            await self.bleak_client.disconnect()  # type: ignore

    @property
    def is_connected(self) -> bool:
        return self.bleak_client.is_connected

    async def supports_service(self, uuid) -> bool:
        return bool(await self.get_service(uuid))

    async def get_service(self, uuid) -> BleakGATTService:
        return self.bleak_client.services.get_service(uuid)

    async def write_characteristic(self, service: BleakGATTService,  data: bytearray, characteristic_uuid: str, response: bool = False) -> None:
        if service is None:
            raise Exception('Service not initialized')
        characteristic = service.get_characteristic(characteristic_uuid)
        if characteristic is None or "write" not in characteristic.properties:
            raise Exception(f'Characteristic: {characteristic_uuid} not found or not writable')
        logging.debug(f'writing characteristic: {characteristic} {characteristic.properties}')
        result = await self.bleak_client.write_gatt_char(characteristic.uuid, data, response)
        return result

    async def subscribe_to_characteristics(self, characteristics: list[str], notification_handler: Callable) -> None:
        self.subscriptions = []
        if self.is_connected:
            logging.debug('Subscribing to characteristics')
            for characteristic in characteristics:
                logging.debug(f'Subscribe to: {characteristic}')
                await self.bleak_client.start_notify(characteristic, notification_handler)
                self.subscriptions.append(characteristic)

    async def unsubscribe_to_characteristics(self):
        if self.is_connected and len(self.subscriptions) > 0:
            logging.debug('Unsubscribing to characteristics')
            for subscription in self.subscriptions:
                logging.debug(f'Unsubscribe from: {subscription}')
                await self.bleak_client.stop_notify(subscription)
            self.subscriptions = []

    def __disconnected(self, client: BleakClient):
        self.mlm_client_disconnected.emit()
        logging.debug(f'Disconnected from device: {self.device.name} {self.device.address}')
        #print('Disconnected from MLM2PRO device, please ensure MLM2PRO is still rumning and connected to the PC. If not please restart the MLM2PRO, wait till there is a steady red light, and resart the connection.')