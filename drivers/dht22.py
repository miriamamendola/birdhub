@native_c("_read_temp", ["csrc/dht.c"], [])
def _read(pin):
    pass

import gpio

class DHT22():
    def __init__(self, pin):
        self.temperature = 0.0
        self.humidity = 0.0
        self.pin = pin
    
    def read(self):
        #BUG la prima lettura mi dà sempre il doppio, perchè?
        self.humidity, self.temperature = _read(self.pin)
        return (self.humidity, self.temperature)