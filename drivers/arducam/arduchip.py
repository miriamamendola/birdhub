from bsp import board
import spi
import gpio
# this file contains spi protocol

# ARDUCHIP REGISTERS
TEST_REGISTER = 0x00
FIFO_CONTROL_REGISTER = 0x04
BURST_FIFO_READ = 0x3C
SINGLE_FIFO_READ = 0x3D
VERSION_REGISTER = 0x40
STATUS_REGISTER = 0x41
FIFO_SIZE = 0x42

class Arduchip():
    def __init__(self, nss=D5):
        self.port = spi.Spi(nss,spi=SPI1, clock=8000000,mode=0)

    def write_reg(self, addr, data):
        # aggiungo bit 1 per indicare scrittura registro
        address = addr | 0x80 
        self.port.select()
        self.port.write(bytearray([address]))
        self.port.write(bytearray([data]))
        self.port.unselect()

    def read_reg(self, addr):
        # annullo il bit 0
        address = addr & 0x7f 
        self.port.select()
        self.port.write(bytearray([address])) 
        rx, _ = self.port.exchange(bytearray([0x00]))
        self.port.unselect()
        return rx


    def flush_fifo(self):
        """
        bit[5] write 1 to reset fifo read pointer
        """
        reg = self.read_reg(FIFO_CONTROL_REGISTER)
        reg = reg | (1 << 5)
        self.write_reg(FIFO_CONTROL_REGISTER, reg)

    def start_capture(self):
        """
        bit[1] write 1 to start capture
        """
        self.write_reg(FIFO_CONTROL_REGISTER, 0x02)
    
    def clear_fifo_flag(self):
        reg = self.read_reg(FIFO_CONTROL_REGISTER)
        reg = reg | 1
        self.write_reg(FIFO_CONTROL_REGISTER, reg)

    def read_fifo_length(self):
        buf = []
        buf.append(self.read_reg(0x42))
        buf.append(self.read_reg(0x43))
        buf.append(self.read_reg(0x44))
        
        length = (buf[2] << 16) | (buf[1] << 8) | buf[0]
        return length

   

    def is_write_fifo_done(self):
        """returns True if bit[3] of status register is 1"""
        reg = self.read_reg(STATUS_REGISTER)
        return True if ((reg & 0x08) >> 3) == 1 else False

    def take_photo(self):
        print("Starting capture")
        # issuing start capture
        self.flush_fifo()
        self.clear_fifo_flag()
        self.start_capture()    

        while self.is_write_fifo_done() == False:
            sleep(1000)

        print("Capture done")
        return self.read_fifo_burst()

    def read_fifo_burst(self):
        length = self.read_fifo_length()
        print("Buffer length:", length)
        if length == 0:
            raise IOError
        
        print("Starting burst FIFO read")
        self.port.select()
        self.port.exchange(bytearray([BURST_FIFO_READ]))
        
        last = curr = 0
        buf = bytearray()
        while length >= 0:
            # leggo il byte corrente e salvo il precedente
            last = curr
            curr, _ = self.port.exchange(bytearray([0x00]))
            # aggiungo al buffer
            buf.append(curr)
            # se rilevo EOI termino
            if curr == 0xD9 and last == 0xFF:
                print("EOI Found!")
                break
            length = length - 1
        
        self.port.unselect()
        return buf