import i2c

class OV2640(i2c.I2c):
    def __init__(self):
        self.port = i2c.I2c(addr=0x30, clock=400000)
        pass

    def write_reg(self, addr, data):
        """
        1. inviare il registro su cui scrivere
        2. inviare i dati da scrivere
        """
        self.port.write(bytearray([addr, data]))

    def read_reg(self, addr):
        self.port.write(bytearray([addr]))
        reg, _ = self.port.write_read(bytearray([addr]), 1)
        return reg
