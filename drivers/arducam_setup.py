from drivers.arducam import config, arduchip, OV2640

def init_camera(arduchip : arduchip.Arduchip, internal_sensor : OV2640.OV2640) -> None:
    """Questa funzione inizializza la comunicazione SPI e il sensore interno.

    Inizialmente, viene verificato il funzionamento dell'interfaccia SPI e dell'interfaccia I2C
    leggendo all'interno di registri di cui il contenuto è noto. Dopo aver eseguito il reset del sensore
    interno, questo viene configurato attraverso le tuple contenute nel file config.py.
    """
    print("Checking SPI BUS...")
    t = 0
    while t != 0x55:
        arduchip.write_reg(0x00, 0x55)
        t = arduchip.read_reg(0x00)
        # print(t)
    print("SPI BUS is ok")

    print("Checking internal sensor...")
    vid = pid = 0
    while ((vid != 0x26) and (pid != 0x41)):
        internal_sensor.write_reg(0xff, 0x01)
        vid = internal_sensor.read_reg(0x0A)
        pid = internal_sensor.read_reg(0x0B)
    print("Internal sensor is ready")

    print("Internal sensor reset...")
    internal_sensor.write_reg(0xff, 0x01)
    internal_sensor.write_reg(0x12, 0x80)

    print("Internal sensor configuration 1/4 [JPEG]...")
    for reg in config.JPG_INIT:
        internal_sensor.write_reg(reg[0], reg[1])

    print("Internal sensor configuration 2/4 [JPEG]...")
    for reg in config.JPG_YUV:
        internal_sensor.write_reg(reg[0], reg[1])

    print("Internal sensor configuration 3/4 [JPEG]...")
    for reg in config.JPG_CONF:
        internal_sensor.write_reg(reg[0], reg[1])

    internal_sensor.write_reg(0xff, 0x01)
    internal_sensor.write_reg(0x15, 0x00)

    print("Internal sensor configuration 4/4 [320x240]...")
    for reg in config.JPG_RES:
        internal_sensor.write_reg(reg[0], reg[1])
        