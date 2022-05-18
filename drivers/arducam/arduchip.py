from bsp import board
import spi
import gpio

# ARDUCHIP REGISTERS
TEST_REGISTER = 0x00
FIFO_CONTROL_REGISTER = 0x04
BURST_FIFO_READ = 0x3C
SINGLE_FIFO_READ = 0x3D
VERSION_REGISTER = 0x40
STATUS_REGISTER = 0x41
FIFO_SIZE = 0x42

class Arduchip():
    """Classe per la gestione della fotocamera.
    
    La comunicazione con l'Arduchip, ossia il chip interno della fotocamera, avviene 
    tramite protocollo SPI. I dettagli implementativi di questa libreria sono stati
    ricavati dalla software application.
    (Software Application)[https://www.arducam.com/downloads/shields/ArduCAM_Camera_Shield_Software_Application_Note.pdf] 
    """
    def __init__(self, nss=D5):
        self.port = spi.Spi(nss,spi=SPI1, clock=8000000,mode=0)

    def write_reg(self, addr:int, data:int) -> None:
        """Metodo per scrivere su un registro dell'Arduchip.

        L'indirizzo passato come parametro viene corretto aggiungendo il bit 1 come MSB, 
        come da specifica.

        Args:
            addr: indirizzo del registro da scrivere.
            data: stringa di bit da scrivere codificata come un intero.
        """
        address = addr | 0x80 
        self.port.select()
        self.port.write(bytearray([address]))
        self.port.write(bytearray([data]))
        self.port.unselect()

    def read_reg(self, addr:int)->int:
        """Metodo per leggere da un registro dell'Arduchip.

        L'indirizzo passato come parametro viene corretto impostando l'MSB a 0, 
        come da specifica.

        Args:
            addr: l'indirizzo del registro da cui leggere.
        
        Returns:
            Il contenuto del registro codificato come un intero.
        """
        address = addr & 0x7f 
        self.port.select()
        self.port.write(bytearray([address])) 
        rx, _ = self.port.exchange(bytearray([0x00]))
        self.port.unselect()
        return rx

    def flush_fifo(self):
        """Metodo per svuotare il buffer FIFO dell'Arduchip.
        
        Per svuotare il buffer è necessario impostare il bit 5 del `FIFO control register` a 1.
        """
        reg = self.read_reg(FIFO_CONTROL_REGISTER)
        reg = reg | (1 << 5)
        self.write_reg(FIFO_CONTROL_REGISTER, reg)

    def start_capture(self):
        """Metodo per scattare una foto.
        
        Per scattare una foto è necessario impostare il bit 1 del `FIFO control register` a 1.
        """
        self.write_reg(FIFO_CONTROL_REGISTER, 0x02)
    
    def clear_fifo_flag(self):
        """Metodo per azzerare la FIFO write done flag.
        
        Per azzerare la FIFO write done flag è necessario impostare il bit 0 del 
        `FIFO control register` a 1.
        """
        reg = self.read_reg(FIFO_CONTROL_REGISTER)
        reg = reg | 1
        self.write_reg(FIFO_CONTROL_REGISTER, reg)

    def read_fifo_length(self) -> int:
        """Metodo per leggere la lunghezza del buffer.

        La lettura avviene richiedendo la lettura di tre registri consecutivi e 
        concatenando i byte letti, considerando che il registro 0x42 contiene i bit [7:0],
        il registro 0x43 contiene i bit [15:8] e il registro 0x44 contiene i bit [22:16].

        Returns:
            Il numero di byte contenuti all'interno del buffer.
        """
        buf = []
        buf.append(self.read_reg(0x42))
        buf.append(self.read_reg(0x43))
        buf.append(self.read_reg(0x44))
        
        length = (buf[2] << 16) | (buf[1] << 8) | buf[0]
        return length

    def is_write_fifo_done(self) -> bool:
        """Metodo usato per controllare lo stato della flag write FIFO done.
        
        La flag `write FIFO done` viene asserita quando la fotocamera ha terminato la cattura
        e il conseguente caricamento nel buffer.

        Returns:
            True se il bit è asserito, False altrimenti.
        """
        reg = self.read_reg(STATUS_REGISTER)
        return True if ((reg & 0x08) >> 3) == 1 else False

    def take_photo(self):
        """Metodo di "interfaccia" per scattare una foto.

        Questo metodo scatta una foto, attende il caricamento nel buffer e richiama
        la funzione di lettura dal buffer.

        Returns:
            La foto codificata come bytearray letta dal buffer.
        """
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
        """Metodo per leggere dal buffer usando la modalità _burst_.

        Il sensore interno della fotocamera viene impostato, per questa specifica applicazione,
        per restituire una foto in JPEG. Un file JPEG ha il marker EOI che segnala la fine dell'immagine.
        Questo marker è composto da due byte (0xFF, 0xD9). La lettura del buffer avviene
        fintanto che la lunghezza del buffer non è esaurita oppure è stato letto l'EOI. 

        Returns:
            La foto codificata come bytearray letta dal buffer.
        """
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