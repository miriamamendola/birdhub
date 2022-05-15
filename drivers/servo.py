### SERVOMOTORE
import gpio
import pwm
# TODO angolo come parametro di configurazione del sistema
PIN_SERVO = D25

# parametro di configurazione (l'angolo non è perfettamente 90 gradi, se lo calibro si
# 1500 è un buon valore)

class Servo():
    def __init__(self, pin=PIN_SERVO):
        self.pin = pin
        self.period = 20000
        self.K = 1500
        gpio.mode(self.pin, OUTPUT)
        pass
    def rotate_and_go_back(self, angle, wait_time=1000):
        # rotazione di un certo angolo per l'apertura del buco
        # commentare
        pulse = 1500 + int(angle * self.K/180)
        #
        print("Apertura")
        pwm.write(self.pin, self.period, 1500, time_unit=MICROS)
        sleep(wait_time)
        print("Chiusura")
        pwm.write(self.pin, self.period, pulse, time_unit=MICROS)
        sleep(1000)
        pwm.write(self.pin, 0, 0)
        pass
