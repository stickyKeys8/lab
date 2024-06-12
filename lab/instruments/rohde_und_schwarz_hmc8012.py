from lab.instruments.scpi_instrument import SCPICommand, SCPIInstrument


class RohdeUndSchwarzHMC8012(SCPIInstrument):
    """Actually a former Hameg model, that I bought on eBay"""

    class SystemCommands(SCPICommand):
        FETCH = "FETC"
        READ = "READ"

    class TriggerCommands(SCPICommand):
        MODE = "TRIG:MODE"

    class MeasurementCommands(SCPICommand):
        MEAUSRUE_VOLTAGE_DC = "MEAS:VOLT:DC"
        MEASURE_TEMP = "MEAS:TEMP"

    def __init__(self, connection) -> None:
        super(RohdeUndSchwarzHMC8012, self).__init__(connection)

    def fetch(self) -> float:
        return float(self._transmit(self.SystemCommands.FETCH))

    def read(self) -> float:
        return float(self._transmit(self.SystemCommands.READ))

    def get_trigger_mode(self) -> str:
        return self._transmit(self.TriggerCommands.MODE)

    def set_trigger_mode(self, mode: str) -> None:
        """
        Modes: SING, AUTO, MAN
        """
        self._write(self.TriggerCommands.MODE, mode)

    def measure_voltage_dc(self, voltage_range: str) -> float:
        """
        Ranges: 400mV, 4V, 40V, 400V, 750V, AUTO , MIN , MAX , DEF

        If the input signal is greater than can be measured on the selected range (manual ranging), the instrument returns 9.90000000E+37.
        """
        return float(
            self._transmit(self.MeasurementCommands.MEAUSRUE_VOLTAGE_DC, voltage_range)
        )

    def measure_temperature(self, enable_4w: bool = False, probe_type: str ="") -> float:
        """
        Probe types: PT100, PT500, PT1000

        If the input signal is greater than can be measured on the selected range (manual ranging), the instrument returns 9.90000000E+37.
        """
        return float(
            self._transmit(self.MeasurementCommands.MEASURE_TEMP, params=f"{'FRTD' if enable_4w else 'RTD'} {probe_type}")
        )


class RohdeUndSchwarzHMC8012_146(RohdeUndSchwarzHMC8012):
    IP_ADDRESS = "192.168.1.146"
