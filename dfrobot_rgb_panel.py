from busio import I2C
from adafruit_bus_device import i2c_device
from micropython import const
import time


class Panel:
    """
    Represents a single RGB panel made up of 16*8 RGB LEDs from DFROBOT. This class provides
    some basic functionality for controlling the panel.
    :param i2c: The I2C bus to use.
    :param int address: The I2C address of the panel.
    :param bool auto_write: True if the display should immediately change when
        set. If False, `show` must be called explicitly.
    ..note:: this class is not provided by DFROBOT, you need to get it from the internet.
    Example:
    .. code-block:: python
        import board
        import busio
        from dfrobot_rgb_panel import Panel
        i2c = busio.I2C(board.SCL, board.SDA)
        panel = Panel(i2c)
        panel.print("Hello World", Panel.RED)
    """

    write_reg = 0x02
    COLOR = 0x03
    PIX_X = 0x04
    PIX_Y = 0x05
    BITMAP = 0x06
    STR = 0x07

    UNCLEAR = 0x0
    CLEAR = 0x1
    Left = 0x0 << 1
    Right = 0x01 << 1

    UNSCROLL = 0x0 << 2
    SCROLL = 0x1 << 2
    PIX_ENABLE = 0x01 << 3
    BITMAP_ENABLE = 0x10 << 3
    STR_ENABLE = 0x11 << 3

    QUENCH = 0
    RED = 1
    GREEN = 2
    YELLOW = 3
    BLUE = 4
    PURRPLE = 5
    CYAN = 6
    WHITE = 7
    SIZE = 50

    def auto_write(self, auto_write: bool) -> None:
        if isinstance(auto_write, bool):
            self._auto_write = auto_write
        else:
            raise ValueError("Must set to either True or False.")

    def __init__(
        self,
        i2c: I2C = None,
        auto_write: bool = True,
        address=0x10,
    ) -> None:
        if i2c is None:
            print('Usage: require I2C instance parameter')
            return

        self._RGBAddress = address
        self._i2c = i2c
        self.i2c_device = [i2c_device.I2CDevice(self._i2c, self._RGBAddress)]
        self._temp = bytearray(1)
        # 设置缓冲区大小，_buffer[0]为功能寄存器
        self._buffer_size = 17
        self._buffer = bytearray((self._buffer_size) * len(self.i2c_device))
        self._auto_write = auto_write

        # self.sys_disable()
        # time.sleep(0.1)
        # self.sys_enable()

    def sys_disable(self):
        self._buffer[0] = Panel.write_reg
        self._buffer[1] = 0x0
        self._buffer[2] = 0x0
        self._buffer[3] = 0x0
        if self._auto_write:
            self.show()

    def sys_enable(self):
        self._buffer[0] = Panel.write_reg
        self._buffer[1] = 0x0
        self._buffer[2] = 0x1
        self._buffer[3] = 0x0
        if self._auto_write:
            self.show()

    def setBrightness(level):
        pass

    def scroll(self, direction):
        if direction is not None and direction != Panel.Right and direction != Panel.Left:
            print('Usage: direction must be Panel.Right or Panel.Left')
            return
        if direction is None:
            self._buffer[1] &= (~(0x01 << 2))
        elif direction == Panel.Right:
            self._buffer[1] |= (0x01 << 2) | (0x01 << 1)
        elif direction == Panel.Left:
            self._buffer[1] |= (0x01 << 2) & (~(0x01 << 1))
        else:
            return
        if self._auto_write:
            self.show()

    # 通过picIndex显示内建的图片

    def display(self, picIndex, color):
        self._buffer[0] = Panel.write_reg  # 0x02
        self._buffer[1] = (self._buffer[1] & (0xe6)) | (0x02 << 3)
        self._buffer[2] = color
        self._buffer[4] = picIndex
        if self._auto_write:
            self.show()

    def print(self, text, color):
        length = len(text)
        if (length > Panel.SIZE):
            print('Usage: text length must be less than 50')
            return
        self._buffer[0] = Panel.write_reg  # 0x02
        self._buffer[1] = (self._buffer[1] & (0xe6)) | (0x03 << 3)
        self._buffer[2] = color
        for i in range(length):
            self._buffer[6 + i] = ord(text[i])
        if self._auto_write:
            self.show()

    def pixel(self, x, y, color):
        self._buffer[0] = Panel.write_reg  # 0x02
        self._buffer[1] = (self._buffer[1] & (0xe6)) | (0x01 << 3)
        self._buffer[2] = color
        self._buffer[3] = x
        self._buffer[4] = y
        if self._auto_write:
            self.show()

    def fillScreen(self, color):
        # 设置功能寄存器为填充屏幕
        self._buffer[0] = Panel.write_reg  # 0x02
        # 设置颜色数据
        self._buffer[1] = 0x01
        self._buffer[1] = (self._buffer[1] & (0xe7)) | (0x01 << 3)
        self._buffer[2] = color
        self._buffer[3] = 0x00
        self._buffer[4] = 0x00
        if self._auto_write:
            self.show()

    def clear(self):
        self._buffer[0] = Panel.write_reg  # 0x02
        self._buffer[1] = 0x01
        self._buffer[2] = 0x0
        if self._auto_write:
            self.show()

    def readReg(reg, num):
        pass

    def show(self) -> None:
        """Refresh the display and show the changes."""
        for index, i2c_dev in enumerate(self.i2c_device):
            with i2c_dev:
                # Byte 0 is 0x00, address of LED data register. The remaining 16
                # bytes are the display register data to set.
                offset = index * self._buffer_size
                buffer = self._buffer[offset: offset + self._buffer_size]
                i2c_dev.write(buffer)
