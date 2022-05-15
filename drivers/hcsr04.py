# SENSORE A ULTRASUONI
import gpio 

@c_native("_read_time", ["csrc/hcsr04.c"], [])
def _read(trig_pin, echo_pin):
    pass

class HCSR04():
    """Classe per la gestione del sensore a ultrasuoni HCSR04.
    (Datasheet Link)[https://cdn.sparkfun.com/datasheets/Sensors/Proximity/HCSR04.pdf]
    """
    def __init__(self, trig_pin, echo_pin):
        self.trig_pin = trig_pin
        self.echo_pin = echo_pin

    def get_distance(self, speed=340) -> float:
        """"Calcola la distanza da un ostacolo in centimetri.
        Args:
            speed (float): la velocità del suono nel mezzo di riferimento.
        Returns:
            float: la distanza in centimetri da un ostacolo.
        """
        return (_read(self.trig_pin, self.echo_pin) * speed)/(2*10000)