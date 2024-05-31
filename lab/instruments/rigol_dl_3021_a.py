from lab.instruments.scpi_instrument import SCPICommand, SCPIInstrument


class RigolDL3021A(SCPIInstrument):
    """Actually a former Hameg model, that I bought on eBay"""

    def __init__(self, connection) -> None:
        super(RigolDL3021A, self).__init__(connection)


class RigolDL3021A_247(RigolDL3021A):
    IP_ADDRESS = "192.168.1.247"
    TCPIP_INSTRUMENT_STRING = f"TCPIP::{IP_ADDRESS}::INSTR"
