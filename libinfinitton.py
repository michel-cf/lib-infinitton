import ctypes
import threading
import time
from typing import Callable

import hid
from PIL import Image
from event_emitter import events

KEYS = {
    (1, 0): 0,
    (2, 0): 1,
    (4, 0): 2,
    (8, 0): 3,
    (16, 0): 4,

    (32, 0): 5,
    (64, 0): 6,
    (128, 0): 7,
    (0, 1): 8,
    (0, 2): 9,

    (0, 4): 10,
    (0, 8): 11,
    (0, 16): 12,
    (0, 32): 13,
    (0, 64): 14,
}

NUM_KEYS = 15
PAGE_PACKET_SIZE = 8017
ICON_SIZE = 72
NUM_TOTAL_PIXELS = 72 * 72

PAGE_1_HEADER = bytearray(
    [0x02, 0x00, 0x00, 0x00, 0x00, 0x40, 0x1f, 0x00, 0x00, 0x55, 0xaa, 0xaa, 0x55, 0x11, 0x22, 0x33,
     0x44, 0x42, 0x4d, 0xf6, 0x3c, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x36, 0x00, 0x00, 0x00, 0x28,
     0x00, 0x00, 0x00, 0x48, 0x00, 0x00, 0x00, 0x48, 0x00, 0x00, 0x00, 0x01, 0x00, 0x18, 0x00, 0x00,
     0x00, 0x00, 0x00, 0xc0, 0x3c, 0x00, 0x00, 0x13, 0x0b, 0x00, 0x00, 0x13, 0x0b, 0x00, 0x00, 0x00,
     0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
PAGE_2_HEADER = bytearray(
    [0x02, 0x40, 0x1f, 0x00, 0x00, 0xb6, 0x1d, 0x00, 0x00, 0x55, 0xaa, 0xaa, 0x55, 0x11, 0x22, 0x33, 0x44])


class InvalidValueException(Exception):
    """
    Exception that will be thrown when a value is provided that is out of range.
    """
    pass


class Infinitton(events.EventEmitter):
    """
    Class to work with an Infinitton screen display. Allowing listening to key presses and setting images on the keys.

    To listen to any of the events add an event listener to the instance. Valid event types are: 'down' and 'up'.
    """

    @staticmethod
    def check_rgb_value(value: int) -> None:
        """
        Check a value intended to be used as an r/g/b value to be shown on the display. Valid values are 0 - 255.
        """
        if value < 0 or 255 < value:
            raise InvalidValueException

    @staticmethod
    def check_valid_key_index(key_index: int) -> None:
        """
        Check a key_index that is intended to be used. Valid values are 0 - 14.
        """
        if key_index < 0 or 14 < key_index:
            raise InvalidValueException

    @classmethod
    def is_present(cls, vid=0xffff, pid=0x1f40) -> bool:
        """
        Check if an Infinitton keyboard is connected. Can be used to check other devices by providing a different
        vid and pid.

        Returns True if the device is present, False otherwise.
        """
        for device in hid.enumerate(vid=vid, pid=pid):
            return True
        return False

    def __init__(self, vid=0xffff, pid=0x1f40):

        events.EventEmitter.__init__(self)
        self._vid = vid
        self._pid = pid
        self._device = None
        self._listening = False
        self._key_states = [False] * 15
        self._listener = _DeviceListener(self)

        self.connect()

    def connect(self) -> bool:
        """
        Call this method before doing any other calls. This will connect to the Infinitton device and start the event-
        loop. Once this is successfully called down and up events can be triggered by pressing on the keyboard.

        Returns True if it was possible to connect to the device. False otherwise.
        """
        try:
            self._device = hid.Device(vid=self._vid, pid=self._pid)
            self._listening = True
            self._start_listening()

            return True
        except hid.HIDException as hide:
            return False

    def disconnect(self) -> None:
        """
        Call this method at the end. Once this method has been called no more communication is possible with the
        keyboard and no events will be triggered.
        """
        if self._device is not None:
            self._listening = False
            self._device.close()
            self._device = None

    def _start_listening(self) -> None:
        self._listener.start()

    def _press(self, key_index: int, key_pressed: bool):
        if self._key_states[key_index] != key_pressed:
            self._key_states[key_index] = key_pressed
            if key_pressed:
                self.emit('down', key_index)
            else:
                self.emit('up', key_index)

    def fill_color(self, key_index: int, r: int, g: int, b: int) -> None:
        """
        Fill the given key with a solid color provided with values r,g and b.
        """
        Infinitton.check_valid_key_index(key_index)

        Infinitton.check_rgb_value(r)
        Infinitton.check_rgb_value(g)
        Infinitton.check_rgb_value(b)

        # self._device.
        pixel = bytearray([b, g, r])
        self._send_image(key_index, pixel * NUM_TOTAL_PIXELS)

    def fill_image_path(self, key_index, image_path) -> None:
        """
        Load an image with the given path and show it on the given key.
        """
        self.fill_image(key_index, Image.open(image_path))

    def fill_image(self, key_index, image: Image) -> None:
        """
        If you want to draw the image in memory, or have it loaded before using Pillow you can use this method to show
        it on the given key.
        """
        Infinitton.check_valid_key_index(key_index)

        if image.width != ICON_SIZE or image.height != ICON_SIZE:
            image = image.resize((ICON_SIZE, ICON_SIZE))

        image = image.transpose(Image.FLIP_TOP_BOTTOM)

        data = bytearray()
        for r in range(ICON_SIZE):
            row_data = bytearray(ICON_SIZE * 3)

            for c in range(ICON_SIZE):
                pixel = image.getpixel((r, c))
                pixel_data_start = 3 * c

                row_data[pixel_data_start] = pixel[0]
                row_data[pixel_data_start + 1] = pixel[1]
                row_data[pixel_data_start + 2] = pixel[2]

            row_data.reverse()
            data += row_data
        self._send_image(key_index, data)

    def _send_image(self, key_index: int, data: bytearray):
        self._send_data_page(PAGE_1_HEADER, data[:7946])
        self._send_data_page(PAGE_2_HEADER, data[7946:])
        self._device.send_feature_report(Infinitton._to_c_char_p(
            bytearray([0x00, 0x12, 0x01, 0x00, 0x00, key_index + 1, 0x00, 0x00,
                       0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                       0x00, 0xf6, 0x3c, 0x00, 0x00, 0x00, 0x00, 0x00,
                       0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])))
        # delay is required, faster update corrupts shown images
        time.sleep(.001)

    def clear_key(self, key_index) -> None:
        """
        Clear the given key (make it black).
        """
        self.fill_color(key_index, 0, 0, 0)

    def clear_all_keys(self) -> None:
        """
        Clear all keys (make them black).
        """
        for key in range(NUM_KEYS):
            self.clear_key(key)

    def _send_data_page(self, header: bytearray, data: bytearray) -> None:
        actual_data = Infinitton._pad_to_length(header + data, PAGE_PACKET_SIZE)
        self._device.write(Infinitton._to_c_char_p(actual_data))

    @staticmethod
    def _pad_to_length(buffer, pad_length):
        return buffer + bytearray([0] * (pad_length - len(buffer)))

    @staticmethod
    def _to_c_char_p(data: bytearray):
        return (ctypes.c_char * (len(data))).from_buffer(data)

    def on(self, event: str, listener: Callable[[int], None]):
        """
        Add event listener. Valid event codes are 'down' and 'up'.
        """
        events.EventEmitter.on(self, event, listener)


# noinspection PyProtectedMember
class _DeviceListener(threading.Thread):

    def __init__(self, parent: Infinitton):
        threading.Thread.__init__(self, daemon=True)
        self._parent = parent

    def run(self) -> None:
        if self._parent._device is not None:
            while self._parent._listening:
                r = self._parent._device.read(3)
                for key_signature, key_index in KEYS.items():
                    if key_signature[1] == 0 and r[2] == 0:
                        # first 8
                        self._parent._press(key_index, key_signature[0] & r[1])

                    elif key_signature[0] == 0 and r[1] == 0:
                        # last 7
                        self._parent._press(key_index, key_signature[1] & r[2])


if __name__ == '__main__':
    INTERVAL = int(255 / 4)
    COLOR_VALUES = [0, INTERVAL, INTERVAL*2, INTERVAL*3, 255]

    def down(button):
        print('down: %s' % button)


    def up(button):
        print('up: %s' % button)


    Infinitton.is_present(0, 0)
    infinitton = Infinitton()

    infinitton.on('down', down)
    infinitton.on('up', up)

    infinitton.clear_all_keys()
    #time.sleep(.005)
    #infinitton.fill_color(0, 255, 0, 0)

    infinitton.fill_image_path(0, 'test/folder.png')

    #for key in range(NUM_KEYS):
    #    infinitton.fill_color(key, COLOR_VALUES[int(key / 5)], COLOR_VALUES[int(key % 5)], COLOR_VALUES[key % 5])
    #    time.sleep(.005)

    time.sleep(60)

    infinitton.disconnect()
