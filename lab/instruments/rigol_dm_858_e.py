from lab.instruments.scpi_instrument import SCPICommand, SCPIInstrument


class RigolDM858E(SCPIInstrument):
    """New Multimeter :)"""

    def __init__(self, connection) -> None:
        super(RigolDM858E, self).__init__(connection)

    class SystemCommands(SCPICommand):
        FETCH = "FETC"
        READ = "READ"

    def fetch(self) -> float:
        return self.read() # TODO

    def read(self) -> float:
        return float(self._transmit(self.SystemCommands.READ))


class RigolDM858E_237(RigolDM858E):
    IP_ADDRESS = "192.168.1.237"
    TCPIP_INSTRUMENT_STRING = f"TCPIP::{IP_ADDRESS}::INSTR"
