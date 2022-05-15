#include "zerynth.h"

C_NATIVE(_read_weight){
    C_NATIVE_UNWARN();
    int dt_pin, sck_pin, gain = 1, bit =0, filler = 0x00;
    uint8_t data[3] = {0}; // 3*8 = 24
    int weight = 0;
    PYC_CHECK_ARG_INTEGER(0);
    PYC_CHECK_ARG_INTEGER(1);
    PYC_CHECK_ARG_INTEGER(2);


    dt_pin = PYC_ARG_INT(0);
    sck_pin = PYC_ARG_INT(1);
    gain = PYC_ARG_INT(2);


    if(gain == 1 || gain == 128){
        gain = 1;
    }else if(gain == 2 || gain == 64){
        gain = 3;
    }else{
        return ERR_IOERROR_EXC;
    }

    RELEASE_GIL();
        
    vhalPinSetMode(dt_pin, PINMODE_INPUT_PULLNONE, EXT_INTR_DISABLE);
    vhalPinSetMode(sck_pin, PINMODE_OUTPUT_PUSHPULL, EXT_INTR_DISABLE);
    while(vhalPinRead(dt_pin) >= 1);
    for(int i = 0; i < 24; i++){
        // clock pulse on sck duration 1 usec
        // alzo il clock
        vhalPinWrite(sck_pin, 1);
        platform_system_wait_micros(1);
        // leggo
        bit = vhalPinRead(dt_pin);
        if(bit >= 1)
            data[i / 8] = data[i/8] | (1 << (7 - i%8));
        // abbasso il clock
        
        vhalPinWrite(sck_pin, 0);
        platform_system_wait_micros(1);
    }
   /*  printf("\n");
    printf("%d %d %d\n", data[0], data[1], data[2]); */

    // 25 (1) sets gain 128, 26 sets gain 32, 27 sets gain 64
    for(int i = 0; i < gain; i++){
        vhalPinWrite(sck_pin, 1);
        platform_system_wait_micros(1);
        vhalPinWrite(sck_pin, 0);
        platform_system_wait_micros(1);
    }
    if(vhalPinRead(dt_pin) != 1){
        printf("INTERNAL LOAD CELL ERROR");
        return ERR_IOERROR_EXC;
    }
    // qualcosa che riguarda l'offset che non so
    ACQUIRE_GIL();

    // numero
        if (data[0] & 0x80) {
		filler = 0xFF;
	} else {
		filler = 0x00;
	}

    weight = filler << 24 | (data[0] << 16) | (data[1] << 8) | data[2];
   

    PInteger *weight_data = pinteger_new(weight);

    MAKE_RESULT(weight_data);

    return ERR_OK;

}