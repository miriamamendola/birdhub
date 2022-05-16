from bsp import board 
import gpio
import adc

class Pump():
    """Classe per la gestione del sistema di approvvigionamento.  
    
    Il sistema è composto da una pompa idraulica, comandata tramite
    output digitale e sensore di livello.
    """
    def __init__(self, pump_pin,level_pin, level_power_pin, max=2140, min=1100):
        self.pump_pin = pump_pin
        self.level_pin = level_pin
        self.level_power_pin = level_power_pin
        self.min = min
        self.max = max
        gpio.mode(self.level_power_pin, OUTPUT)
        gpio.mode(self.pump_pin, OUTPUT)
        gpio.mode(self.level_pin, INPUT_ANALOG)
    
    def get_raw_water_level(self) -> float:
        #gpio.high(self.level_power_pin)
        #sleep(10)
        wl = adc.read(self.level_pin)
        #gpio.low(self.level_power_pin)
        return wl 

    def get_water_level(self) -> float:
        """Metodo per il controllo del livello dell'acqua.

        Poichè il water level sensor soffre di problemi di surriscaldamento,
        viene alimentato solo per il tempo necessario ad eseguire la lettura. 
        
        Returns: 
            float: percentuale d'acqua ottenuta rispetto alla varaibile fondoscala.
        """
        return (self.get_raw_water_level() - self.min) * 100 / (self.max - self.min)

    def pump(self, level:float=80) -> None:
        """Metodo per l'azionamento della pompa.
        
        Args:
            level: il livello d'acqua all'interno della ciotola che si vuole ottenere.
        """
        water_level = self.get_water_level()
        while water_level < level:
            gpio.high(self.pump_pin)
            sleep(500)
            water_level = self.get_water_level()
        gpio.low(self.pump_pin)