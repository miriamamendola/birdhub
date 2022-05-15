#include "zerynth.h"
#include "zerynth_debug.h"
C_NATIVE(_read_time){
    C_NATIVE_UNWARN();
    int trig_pin, echo_pin, mu1, mu2, delta, t_start;

    PYC_CHECK_ARG_INTEGER(0);
    PYC_CHECK_ARG_INTEGER(1);

    trig_pin = PYC_ARG_INT(0);
    echo_pin = PYC_ARG_INT(1);

    vhalPinSetMode(trig_pin,PINMODE_OUTPUT_PUSHPULL,EXT_INTR_DISABLE);
    vhalPinSetMode(echo_pin,PINMODE_INPUT_PULLNONE,EXT_INTR_DISABLE);

    RELEASE_GIL();
    // attivare il pin trigger per 10 usec
    vhalPinWrite(trig_pin, 1);
    vosThSleep(TIME_U(12,MICROS));
    vhalPinWrite(trig_pin, 0);

    // a questo punto il sensore invia 8 cicli di segnale a 40Khz per misurare
    // non appena rilevo il fronte di salita 
    t_start = platform_system_get_micros(); 
    while(vhalPinRead(echo_pin) < 1){
        if(platform_system_get_micros() - t_start > 1000000){
            ZDEBUG("INTERNAL ULTRASOUND ERROR");
            return ERR_TIMEOUT_EXC;
        }
    }
    
    mu1 = platform_system_get_micros();
    while(vhalPinRead(echo_pin) >= 1);
    
    mu2 = platform_system_get_micros();
    delta = mu2 - mu1;
    
    ACQUIRE_GIL();
    PInteger *echo_time = pinteger_new(delta);

    MAKE_RESULT(echo_time);

    return ERR_OK;

}