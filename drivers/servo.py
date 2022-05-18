### SERVOMOTORE
import gpio
import pwm

class Servo():
    """Classe per la gestione del servo SG90. 
    Il servomotore viene comandato tramite PWM. La costante `PERIOD` contiene il 
    periodo con cui emettere il segnale PWM ed è presa dal datasheet. Il parametro `K`
    definisce la variazione rispetto alla posizione di riferimento (in cui la variabile pulse è a
    1500).
    """
    def __init__(self, pin):
        self.pin = pin
        self.PERIOD = 20000
        self.K = 1500
        gpio.mode(self.pin, OUTPUT)

    def rotate_and_go_back(self, angle:int, wait_time:int=1000) -> None:
        """Funzione che aziona il servo.

        Il servo viene ruotato di un certo angolo, `angle`, per versare il mangime all'interno
        del serbatoio, trovandosi in posizione di _apertura_. Dopo un certo tempo di attesa pari 
        a `wait_time`, il servo ritorna nella posizione iniziale, trovandosi in posizione di _chiusura_. 

        Args:
            angle: l'angolo di rotazione del servomotore.
            wait_time: il tempo durante cui il servo deve restare in posizione di _apertura_.
        """

        pulse = 1500 + int(angle * self.K/180)
        print("Apertura")
        pwm.write(self.pin, self.PERIOD, 1500, time_unit=MICROS)
        sleep(wait_time)
        print("Chiusura")
        pwm.write(self.pin, self.PERIOD, pulse, time_unit=MICROS)
        sleep(wait_time)
        pwm.write(self.pin, 0, 0)
    
