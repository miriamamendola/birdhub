import i2c

class OV2640(i2c.I2c):
    """Classe per la gestione della comunicazione con il sensore interno di Arducam.

    La comunicazione con il sensore OV2640 avviene tramite protocollo I2C. Sebbene nella
    Hardware Application Note siano riportati due indirizzi (0x60 per la lettura e 0x61 
    per la scrittura), la comunicazione I2C viene inizializzata tramite l'indirizzo 0x30 e
    la libreria I2C di Zerynth, aggiungendo il bit di scrittura o di lettura, trasforma
    l'indirizzo nel formato corretto.
    """    
    def __init__(self):
        self.port = i2c.I2c(addr=0x30, clock=400000)
        pass

    def write_reg(self, addr:int, data:int) -> None:
        """Funzione per scrivere all'interno di un registro del chip OV2640.
        """
        self.port.write(bytearray([addr, data]))

    def read_reg(self, addr:int) -> int:
        """Funzione per leggere da un registro del chip OV2640.
        """
        self.port.write(bytearray([addr]))
        reg, _ = self.port.write_read(bytearray([addr]), 1)
        return reg
