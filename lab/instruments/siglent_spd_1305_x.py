from lab.instruments.scpi_instrument import SCPICommand, SCPIInstrument


class Siglent1305X(SCPIInstrument):
    """Actually a Siglent 1104X-C that I bought in China."""

    def __init__(self, connection) -> None:
        super(Siglent1305X, self).__init__(connection)


class Siglent1305X_249(Siglent1305X):
    IP_ADDRESS = "192.168.1.249"
