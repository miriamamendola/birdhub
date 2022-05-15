#import "zerynth.h"
#include "zerynth_debug.h"

int _wait_pin(int pin, int micros, int low){
    int cycles = 0;
    if(low){
        while(vhalPinRead(pin) < 1){
            platform_system_wait_micros(1);
            cycles++;
            if(cycles >= micros){
                break;
            }
        }
    }else{
        while(vhalPinRead(pin) >= 1){
            platform_system_wait_micros(1);
            cycles++;
            if(cycles >= micros){
                break;
            }
        }
    }
    
    return cycles;

}


C_NATIVE(_read_temp){
    C_NATIVE_UNWARN();
    int pin, micros = 0;
    uint8_t bits[40][2]={0};
    uint8_t values[5] = {0};
    double temperature = 0.0, humidity = 0.0;

    /* Controllo argomenti */
    PYC_CHECK_ARG_INTEGER(0);

    pin = PYC_ARG_INT(0);
    RELEASE_GIL();
    /* Pull down data line */
    vhalPinSetMode(pin,PINMODE_OUTPUT_PUSHPULL,EXT_INTR_DISABLE);
    vhalPinWrite(pin,0);
    
    vosThSleep(TIME_U(1,MILLIS));
    /* Pull up data line */

    vhalPinWrite(pin, 1);
    vosThSleep(TIME_U(19,MICROS));

    /* Waiting for sensor response */
    vhalPinSetMode(pin,PINMODE_INPUT_PULLUP,EXT_INTR_DISABLE);
    
    micros = _wait_pin(pin, 80, 1);
    micros += _wait_pin(pin, 80, 0);


    /* Sensor starts transmitting */
    for(int i = 0; i < 40; i++){
        bits[i][0] = _wait_pin(pin, 50, 1);
        bits[i][1] = _wait_pin(pin, 80, 0);
    } 
    ACQUIRE_GIL();
    for(int i = 0; i < 40; i++){
        if( bits[i][1] > bits[i][0] ){
            // va nell'elemento dell'array corrispondente 
            // il bit va in or nella posizione corrispondente al modulo
            values[i / 8] = values[i / 8] | (1 << (7 - i%8));
        }
    }
    uint8_t cc = values[0] + values[1] + values[2] + values[3];
    ZDEBUG("%d + %d + %d + %d = %d\n", values[0], values[1], values[2], values[3], values[4]);
    ZDEBUG("Checksum is %d\n", cc);

    if(cc != values[4]){
        ZERROR("Checksum is not correct\n");
        return ERR_IOERROR_EXC;
    }

    /* Conversion, see Adafruit library */
    temperature = (values[2] & 0x7F) << 8 | values[3];
    temperature *= 0.1;

    if (values[2] & 0x80) {
        temperature *= -1;
    }

    humidity = (values[0]) << 8 | values[1];
    humidity *= 0.1;

    /* zOs native types */
    PTuple *data = ptuple_new(2, NULL);
    PTUPLE_SET_ITEM(data,0,pfloat_new(humidity));
    PTUPLE_SET_ITEM(data,1,pfloat_new(temperature));
    MAKE_RESULT(data);
    return ERR_OK;
}
