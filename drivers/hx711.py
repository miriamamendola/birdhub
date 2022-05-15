from bsp import board
import gpio

@c_native("_read_weight", ["csrc/hx711.c"], [])
def _read(dt_pin, sck_pin, gain):
    pass

class HX711():
    """Classe per la gestione del chip HX711, 24-bit ADC per la cella di carico.

    (Datasheet link)[https://cdn.sparkfun.com/datasheets/Sensors/ForceFlex/hx711_english.pdf]

    Dopo l'inizializzazione è opportuno eseguire la calibrazione del sensore tramite le funzioni
    `tare` e `calibrate` per evitare la lettura di valori apparentemente casuali.
    """
    def __init__(self, dt_pin, sck_pin):
        """
        La variabile di istanza offset contiene l'offset da sottrarre alla misura,
        mentre la variabile scale contiene il fattore di scala della misura, da dividere
        alla misura con offset.
        """
        self.dt_pin = dt_pin
        self.sck_pin = sck_pin
        self.scale = 1
        self.offset = 0

    def read(self, gain:int=128) -> float:
        """Fornisce il dato riscalato secondo i parametri impostati.

        Il metodo richiede una lettura al sensore tramite la funzione `_read`. Il dato 
        restituito viene riscalato sottraendo la tara e regolandolo usando il fattore di calibrazione,
        deciso in fase di calibrazione.

        Args:
            gain (int): il guadagno con cui l'HX711 amplifica la lettura dei valori sulla cella di carico.
            I valori accettabili sono: 128 oppure 1 per un guadagno di 128 e 64 oppure 2 per un guadagno di 64.
            Il chip ha anche una modalità con guadagno di 32, ma non è stata supportata da questa implementazione
            del driver in quanto richiede il collegamento fisico al canale B della scheda.
        
        Returns:
            float: la lettura in grammi del peso presente sulla cella di carico.
        """
        return( _read(self.dt_pin, self.sck_pin, gain) - self.offset) / self.scale

    def is_ready(self) -> bool:
        """Testa se la cella di carico è pronta.
        
        Se la cella di carico è pronta, l'HX711 abbassa il bus DT. Il controllo
        dev'essere effettuato continuamente essendo una lettura singola.

        Returns:
            True se la cella di carico è pronta, False altrimenti.

        """
        return gpio.get(self.dt_pin) == LOW

    def average(self, times:int=10) -> float:
        """Funzione di utilità che calcola la media di `times` letture.

        Poichè questa funzione è impiegata per le funzioni di tara e calibrazione
        i dati che restituisce non sono riscalati.
        Args:
            times: Numero di letture da richiedere al sensore.

        Returns:
            La media aritmetica delle `times` letture.
        """
        weight_sum = 0
        for i in range(0, times):
            weight_sum += _read(self.dt_pin, self.sck_pin, 128)
        return weight_sum / times

    def tare(self, times:int=10) -> None:
        """Tara il sensore.

        La funzione consente di tarare il sensore scegliendo l'offset che viene
        impiegato dalla funzione `read`. L'offset viene ottenuto come media delle letture _raw_
        tramite la funzione average.

        Args:
            times: Parametro da passare alla funzione `average`.
        """
        self.offset = self.average(times)

    def calibrate(self, known_weight : float, times : int = 10) -> None:
        """Calibra il sensore.

        La funzione consente di calibrare il sensore determinando il fattore di calibrazione
        impiegato dalla funzione `read`. Prima di chiamare questa funzione è opportuno eseguire la tara
        del sensore. La funzione dev'essere chiamata dopo che un oggetto di peso `known_weight` è stato
        posizionato sulla cella di carico. 
        
        Args:
            known_weight: Il peso in grammi dell'oggetto che viene posizionato sulla cella di carico.
            times: Parametro da passare alla funzione `average`.
        """
        res = self.average(times) - self.offset
        self.scale = res / known_weight