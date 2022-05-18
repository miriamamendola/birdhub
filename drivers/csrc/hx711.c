#include "zerynth.h"
#include "zerynth_debug.h"

C_NATIVE(_read_weight){
    C_NATIVE_UNWARN();
    int dt_pin, sck_pin, gain = 1, bit =0, filler = 0x00;
    /* L'ADC di HX711 lavora a 24 bit */
    uint8_t data[3] = {0};
    int weight = 0;
    PYC_CHECK_ARG_INTEGER(0);
    PYC_CHECK_ARG_INTEGER(1);
    PYC_CHECK_ARG_INTEGER(2);

    dt_pin = PYC_ARG_INT(0);
    sck_pin = PYC_ARG_INT(1);
    gain = PYC_ARG_INT(2);

    /* Controllo dell'argomento gain (può essere solo 1 (128) o 2 (64) */
    if(gain == 1 || gain == 128){
        gain = 1;
    }else if(gain == 2 || gain == 64){
        gain = 3;
    }else{
        ZDEBUG("Gain parameter is incorrect");
        return ERR_IOERROR_EXC;
    }

    /* Rilascio del mutex da parte dell'interprete Python */
    RELEASE_GIL();

    /* Configurazione dei pin */
    vhalPinSetMode(dt_pin, PINMODE_INPUT_PULLNONE, EXT_INTR_DISABLE);
    vhalPinSetMode(sck_pin, PINMODE_OUTPUT_PUSHPULL, EXT_INTR_DISABLE);

    /* Quando HX711 è pronto, viene abbassato il pin DT */
    while(vhalPinRead(dt_pin) >= 1);

    /* Lettura del dato */
    for(int i = 0; i < 24; i++){
        /* Il driver imposta SCK a 1 per 1 usec per richiedere la lettura di un bit */
        vhalPinWrite(sck_pin, 1);
        platform_system_wait_micros(1);
        /* Mentre SCK è alto viene letto un bit dal pin DT*/
        bit = vhalPinRead(dt_pin);
        
        /* Il bit letto viene inserito nella posizione opportuna */
        if(bit >= 1)
            data[i / 8] = data[i/8] | (1 << (7 - i%8));
        
        /* Il driver abbassa SCK al termine della lettura del bit */
        vhalPinWrite(sck_pin, 0);
        platform_system_wait_micros(1);
    }

    /* Settaggio del gain */
    /* I successivi cicli di clock determinano il gain della lettura successiva.
     * Dalla specifica:
     * - 25 cicli impostano il gain a 128 sul canale A
     * - 26 cicli impostano il gain a 32 sul canale B
     * - 27 cicli impostano il gain a 64 sul canale A 
     * Per questa specifica applicazione, il canale B non è supportato. */ 
     
    for(int i = 0; i < gain; i++){
        vhalPinWrite(sck_pin, 1);
        platform_system_wait_micros(1);
        vhalPinWrite(sck_pin, 0);
        platform_system_wait_micros(1);
    }

    /* Se la comunicazione è avvenuta correttamente, il pin DT viene asserito */
    if(vhalPinRead(dt_pin) != 1){
        ZDEBUG("INTERNAL LOAD CELL ERROR");
        return ERR_IOERROR_EXC;
    }

    /* Viene riacquisito il mutex da parte dell'interprete Python */
    ACQUIRE_GIL();

    /* Poichè la misura dell'ADC è in complemento a 2, viene eseguita 
     * l'estensione del segno. */
    if (data[0] & 0x80) {
		filler = 0xFF;
	} else {
		filler = 0x00;
	}

    /* I dati letti vengono concatenati considerando che l'ADC lavora in modalità
     * MSB first. */
    weight = filler << 24 | (data[0] << 16) | (data[1] << 8) | data[2];
   
    PInteger *weight_data = pinteger_new(weight);
    
    /* Viene restituito il dato misurato */
    MAKE_RESULT(weight_data);

    return ERR_OK;

}