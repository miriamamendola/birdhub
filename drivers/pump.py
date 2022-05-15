from bsp import board 
import gpio
import adc

class Pump():
    def __init__(self, pump_pin=D23,level_pin=D35, level_power_pin=D5):
        self.pump_pin = pump_pin
        self.level_pin = level_pin
        self.level_power_pin = level_power_pin
        gpio.mode(self.level_power_pin, OUTPUT)
        gpio.mode(self.pump_pin, OUTPUT)
        gpio.mode(self.level_pin, INPUT_ANALOG)
    
    def get_water_level(self):
        gpio.high(self.level_power_pin)
        sleep(10)
        wl = adc.read(self.level_pin) * 100 / 800
        gpio.low(self.level_power_pin)
        return wl 

    def pump(self, level=80):
        """in ms"""
        water_level = self.get_water_level()
        while water_level < level:
            gpio.high(self.pump_pin)
            sleep(500)
            water_level = self.get_water_level()
        gpio.low(self.pump_pin)
