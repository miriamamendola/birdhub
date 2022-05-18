from bsp import board 
import gpio

class Pump():
    """Classe per la gestione del sistema di approvvigionamento.  
    
    Il sistema è composto da una pompa idraulica, comandata tramite
    output digitale.
    """
    def __init__(self, pump_pin,):
        self.pump_pin = pump_pin
        gpio.mode(self.pump_pin, OUTPUT)


    def pump(self, pump_time : int =1500) -> None:
        """Metodo per l'azionamento della pompa.
        
        Args:
            pump_time: il tempo in cui la pompa deve rimanere attiva durante un ciclo di pompaggio.
        """
        gpio.high(self.pump_pin)
        sleep(pump_time)
        gpio.low(self.pump_pin)
        sleep(pump_time)