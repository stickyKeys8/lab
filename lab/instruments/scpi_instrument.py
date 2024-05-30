from enum import Enum
import time

class SCPICommand(Enum):
    pass

class SCPIInstrument():
    class CommonCommands(SCPICommand):
        ID = "*IDN"
        RESET = "*RST"
        OPERATION_COMPLETE = "*OPC"

    QUERY_SUFFIX = "?"
    COMMAND_SUFFIX = "\r\n"
    PORT = 5025
    POLLING_SLEEP_TIME = 0.1

    def __init__(self, connection):
        self._connection = connection

    def get_id_string(self) -> str:
        return self._transmit(self.CommonCommands.ID)

    def reset(self) -> None:
        self._write(self.CommonCommands.RESET)

    def is_operation_complete(self) -> bool:
        return "1" in self._transmit(self.CommonCommands.OPERATION_COMPLETE)

    def wait_until_operation_is_completed(self) -> None:
        while not self.is_operation_complete():
            time.sleep(self.POLLING_SLEEP_TIME)

    def _read(self) -> str:
        response = b''
        while response[-1:] != b'\n':
            if type(self._connection).__name__ == 'socket':
                response = self._connection.recv(64) #TODO Check amount of bytes
            if type(self._connection).__name__ == 'USBInstrument':
                response = self._connection.read_raw(64) #TODO Check amount of bytes
        return response.decode('ascii').strip()

    def _write(self, command: SCPICommand, params: str = "", query: bool = False):
        cmd = command.value + self.QUERY_SUFFIX if query else command.value
        if type(self._connection).__name__ == 'socket':
            self._connection.sendall((cmd + " " + params + self.COMMAND_SUFFIX).encode())
        if type(self._connection).__name__ == 'USBInstrument':
            self._connection.write(cmd + params)

    def _transmit(self, command: SCPICommand, params: str = "", query: bool = True) -> str:
        self._write(command, params, query)
        return self._read()
