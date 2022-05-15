from bsp import board
import gpio

@c_native("_read_weight", ["csrc/hx711.c"], [])
def _read(dt_pin, sck_pin, gain):
    pass

class HX711():
    def __init__(self, dt_pin, sck_pin):
        self.dt_pin = dt_pin
        self.sck_pin = sck_pin
        self.scale = 1
        self.offset = 0
        self.known_weight = 1

    def read(self, gain=128):
        return( _read(self.dt_pin, self.sck_pin, gain) - self.offset) / self.scale

    def is_ready(self):
        return gpio.get(self.dt_pin) == LOW

    # da testare dopo per risparmiare energia
    def power_down(self):
        gpio.high(self.sck_pin)

    def power_up(self):
        gpio.low(self.sck_pin)

    # TODO funzioni di tara

    def average(self, times=10):
        weight_sum = 0
        for i in range(0, times):
            weight_sum += _read(self.dt_pin, self.sck_pin, 128)
        return weight_sum / times

    def tare(self, times=10):
        self.offset = self.average(times)

    def calibrate(self, times=10):
        res = self.average(times) - self.offset
        self.scale = res / self.known_weight