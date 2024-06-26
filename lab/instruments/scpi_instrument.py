import time
from enum import Enum


class SCPICommand(Enum):
    pass


class SCPIInstrument:
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

    def _read(self, size=64) -> bytes:
        response = b""
        while response[-1:] != b"\n":
            if type(self._connection).__name__ == "Telnet":
                response = self._connection.read_very_eager()
                break
            if type(self._connection).__name__ == "socket":
                response = self._connection.recv(size)
            if type(self._connection).__name__ in ["USBInstrument", "TCPIPInstrument"]:
                response = self._connection.read_raw(size)
        return response

    def _write(self, command: SCPICommand, params: str = "", query: bool = False):
        cmd = command.value + self.QUERY_SUFFIX if query else command.value
        if type(self._connection).__name__ == "Telnet":
            final_cmd = (cmd + " " + params).strip() + self.COMMAND_SUFFIX
            self._connection.write(final_cmd.encode())
        if type(self._connection).__name__ == "socket":
            final_cmd = cmd + " " + params + self.COMMAND_SUFFIX
            self._connection.sendall(final_cmd.encode())
        if type(self._connection).__name__ in ["USBInstrument", "TCPIPInstrument"]:
            final_cmd = str(cmd + " " + params).strip()
            self._connection.write(final_cmd)

    def _transmit(
        self, command: SCPICommand, params: str = "", query: bool = True
    ) -> str:
        self._write(command, params, query)
        return self._read().decode("ascii").strip()
