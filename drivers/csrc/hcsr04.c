#include "zerynth.h"
#include "zerynth_debug.h"
C_NATIVE(_read_time){
    C_NATIVE_UNWARN();

    int trig_pin, echo_pin, mu1, mu2, delta, t_start;

    PYC_CHECK_ARG_INTEGER(0);
    PYC_CHECK_ARG_INTEGER(1);

    trig_pin = PYC_ARG_INT(0);
    echo_pin = PYC_ARG_INT(1);
    
    /* Rilascio del mutex da parte dell'interprete Python */
    RELEASE_GIL();
    
    /* Configurazione dei pin */
    vhalPinSetMode(trig_pin,PINMODE_OUTPUT_PUSHPULL,EXT_INTR_DISABLE);
    vhalPinSetMode(echo_pin,PINMODE_INPUT_PULLNONE,EXT_INTR_DISABLE);
    /* Da specifica, per avviare una lettura è necessario attivare il pin
     * trigger per 10 usec */
    vhalPinWrite(trig_pin, 1);
    vosThSleep(TIME_U(12,MICROS));
    vhalPinWrite(trig_pin, 0);

    /* Al termine dell'attivazione del pin, il sensore invia 8 cicli di
      segnale a ultrasuoni a 40Khz. Quando il segnale ritorna indietro a causa
      di un ostacolo, il sensore imposta a livello logico alto il pin ECHO. 
    */

    /* Si controlla che il tempo in cui il pin ECHO non è asserito sia minore di
     * una certa soglia altrimenti viene lanciata un'eccezione di timeout. */
    t_start = platform_system_get_micros(); 
    while(vhalPinRead(echo_pin) < 1){
        if(platform_system_get_micros() - t_start > 1000000){
            ZDEBUG("INTERNAL ULTRASOUND ERROR");
            return ERR_TIMEOUT_EXC;
        }
    }
    
    /* Non appena viene rilevato un fronte di salita, il ciclo while soprastante 
     * termina e viene salvato l'instante temporale nella variabile mu1. */
    mu1 = platform_system_get_micros();
    while(vhalPinRead(echo_pin) >= 1);
    
    /* Quando viene rilevato il fronte di discesa di ECHO, il ciclo while 
     * soprastante termina e viene salvato l'istante temporale nella variabile mu2 e
     * viene calcolata la differenza tra i due istanti temporali. Questa differenza
     * rappresenta il tempo che l'ultrasuono ha impiegato per raggiungere l'ostacolo
     * e tornare indietro. */
    mu2 = platform_system_get_micros();
    delta = mu2 - mu1;
    
    /* Viene riacquisito il mutex da parte dell'interprete Python */
    ACQUIRE_GIL();
    PInteger *echo_time = pinteger_new(delta);
    /* Viene restituito il dato misurato */
    MAKE_RESULT(echo_time);

    return ERR_OK;

}