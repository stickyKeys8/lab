from lab.instruments.scpi_instrument import SCPICommand, SCPIInstrument


class RigolDL3021A(SCPIInstrument):
    """Actually a former Hameg model, that I bought on eBay"""

    def __init__(self, connection) -> None:
        super(RigolDL3021A, self).__init__(connection)

    class MeasureCommands(SCPICommand):
        VOLTAGE = "MEAS:VOLT"
        CURRENT = "MEAS:CURR"
        POWER = "MEAS:POW"

    class SourceCommands(SCPICommand):
        INPUT = "INP:STAT"
        CURRENT = "CURR:LEV:IMM"

    def measure_voltage(self) -> float:
        return float(self._transmit(self.MeasureCommands.VOLTAGE))

    def measure_current(self) -> float:
        return float(self._transmit(self.MeasureCommands.CURRENT))

    def measure_power(self) -> float:
        return float(self._transmit(self.MeasureCommands.POWER))

    def set_enable_input(self, enable: bool):
        self._write(self.SourceCommands.INPUT, params="ON" if enable else "OFF")

    def get_enable_input(self) -> bool:
        response = self._transmit(self.SourceCommands.INPUT)
        return "1" in response

    def set_current(self, amps: int):
        self._write(self.SourceCommands.CURRENT, params=str(amps))

    def get_current(self) -> float:
        response = self._transmit(self.SourceCommands.CURRENT)
        return float(response)

class RigolDL3021A_247(RigolDL3021A):
    IP_ADDRESS = "192.168.1.247"
    TCPIP_INSTRUMENT_STRING = f"TCPIP::{IP_ADDRESS}::INSTR"
    PORT = 5555
    CURRENT_SETTLING_TIME = 2
