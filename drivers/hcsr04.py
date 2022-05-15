# SENSORE A ULTRASUONI
import gpio 

@c_native("_read_time", ["csrc/hcsr04.c"], [])
def _read(trig_pin, echo_pin):
    pass

class HCSR04():
    def __init__(self, trig_pin, echo_pin):
        self.trig_pin = trig_pin
        self.echo_pin = echo_pin

    def get_distance(self, speed=340):
        """"Restituisce la distanza in cm"""
        return (_read(self.trig_pin, self.echo_pin) * speed)/(2*10000)


