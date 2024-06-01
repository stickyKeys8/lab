from lab.instruments.scpi_instrument import SCPICommand, SCPIInstrument


class Siglent1305X(SCPIInstrument):
    """Actually a Siglent 1104X-C that I bought in China."""

    class MeasureCommands(SCPICommand):
        VOLTAGE = "MEAS:VOLT"
        CURRENT = "MEAS:CURR"
        POWER = "MEAS:POWE"

    class SourceCommands(SCPICommand):
        VOLTAGE = "CH1:VOLT"
        CURRENT = "CH1:CURR"
        POWER = "CH1:POWE"
        OUTPUT_ON = "OUTP CH1,ON" # OUTP CH1,ON  No fucking space between CH1,ON
        OUTPUT_OFF = "OUTP CH1,OFF" # OUTP CH1,ON  No fucking space between CH1,ON
        WAVE_DISPLAY_ON = "OUTP:WAVE CH1,ON" # OUTP CH1,ON  No fucking space between CH1,ON
        WAVE_DISPLAY_OFF = "OUTP:WAVE CH1,OFF" # OUTP CH1,ON  No fucking space between CH1,ON

    class SystemCommands(SCPICommand):
        MODE = "MODE:SET" # Params {2W|4W}
        STATUS = "SYST:STAT" # returns a register check manual

    def __init__(self, connection) -> None:
        super(Siglent1305X, self).__init__(connection)

    def set_voltage(self, volts : float):
        self._write(self.SourceCommands.VOLTAGE, str(volts))

    def get_voltage(self) -> float:
        return float(self._transmit(self.SourceCommands.VOLTAGE))

    def set_current(self, amps: float):
        self._write(self.SourceCommands.CURRENT, str(amps))

    def get_current(self) -> float:
        return float(self._transmit(self.SourceCommands.CURRENT))

    def set_enable_output(self, enable : bool):
        if enable:
            self._write(self.SourceCommands.OUTPUT_ON)
        else:
            self._write(self.SourceCommands.OUTPUT_OFF)

    def get_output_enabled(self) -> bool:
        system_status = self.get_sytem_status()
        bit_mask = 16
        return (int(system_status.decode(), 16) & bit_mask) != 0

    def get_wave_display_enabled(self) -> bool:
        system_status = self.get_sytem_status()
        bit_mask = 256
        return (int(system_status.decode(), 16) & bit_mask) != 0

    def get_4w_mode_enabled(self) -> bool:
        """0 = 2W ; 1 = 4W"""
        system_status = self.get_sytem_status()
        bit_mask = 32
        return (int(system_status.decode(), 16) & bit_mask) != 0

    def set_enable_wave_display(self, enable: bool):
        if enable:
            self._write(self.SourceCommands.WAVE_DISPLAY_ON)
        else:
            self._write(self.SourceCommands.WAVE_DISPLAY_OFF)

    def measure_voltage(self) -> float:
        return float(self._transmit(self.MeasureCommands.VOLTAGE))

    def measure_current(self) -> float:
        return float(self._transmit(self.MeasureCommands.CURRENT))

    def measure_power(self) -> float:
        return float(self._transmit(self.MeasureCommands.POWER))

    def set_mode(self, mode: str):
        """modes: 2W | 4W """
        self._write(self.SystemCommands.MODE, params=mode)

    def get_sytem_status(self):
        self._write(self.SystemCommands.STATUS, query=True)
        return self._read()

class Siglent1305X_249(Siglent1305X):
    IP_ADDRESS = "192.168.1.249"
