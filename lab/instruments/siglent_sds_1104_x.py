import matplotlib.pyplot as plt
from quantiphy import Quantity

from lab.instruments.scpi_instrument import SCPICommand, SCPIInstrument


class Siglent1104X(SCPIInstrument):
    """Actually a Siglent 1104X-C that I bought in China."""

    class CommmonHeaderCommands(SCPICommand):
        HEADER_TYPE = "CHDR"  # SHORT, MEDIUM, LONG

    class AcquisitionCommands(SCPICommand):
        ARM = "ARM"
        STOP = "STOP"
        ACQUIRE_WAY = "ACQW"
        ACQUIRE_AVERAGES = "AVGA"
        MEMORY_SIZE = "MSIZ"
        SAMPLE_STATUS = "SAST"
        SAMPLE_RATE = "SARA"  # For the digital channels use DI:SARA?
        NUMBER_OF_ACQUIRED_SAMPLES = "SANU"  # parameter channel
        SINX_INTERPOLATION = "SXSA"  # parameter ON and OFF
        X_Y_DISPLAY = "XYDS"  # parameter ON and OFF
        AUTO_SETUP = "ASET"
        SCREEN_DUMP = "SCDP"
        WAVEFORM = "C2:WF"
        VDIV = "MTVD"
        OFFSET = "MTVP"
        TDIV = "TDIV"
        # sara = sds.query("sara?")

    class ChannelCommands(SCPICommand):
        ATTENUATION = "ATTN"  # C1:ATTN 100 sets the attenuation to 100:1
        BANDWIDTH_LIMIT = "BWL"  # BWL C1,ON,C2,ON,C3,ON,C4,ON
        COUPLING = "CPL"  # C2:CPL D50  50=50Ohm 1M=1MGOhm D=DC A=AC
        OFFSET = "OFST"  # C2:OFST -3V
        SKEW = "SKEW"  # C1:SKEW 3NS
        TRACE = "TRA"  # C1:TRA ON
        UNIT = "UNIT"  # C1:UNIT V  V=Volt A=Amps
        VOLTS_PER_DIVISION = "VDIV"  # C1:VDIV 50mV
        INVERT = "INVS"  # C1:INVS ON

    class TimeBaseCommands(SCPICommand):
        TIME_DIVISION = "TDIV"

    def __init__(self, connection) -> None:
        super(Siglent1104X, self).__init__(connection)

    def run(self) -> None:
        self._write(self.AcquisitionCommands.ARM)

    def stop(self) -> None:
        self._write(self.AcquisitionCommands.STOP)

    def get_sample_status(self) -> str:
        return self._transmit(self.AcquisitionCommands.SAMPLE_STATUS)

    def set_x_y_display(self, enabled: bool) -> None:
        assert (
            "Stop" not in self.get_sample_status()
        ), "Cannot set x-y display in stop mode!"
        self._write(self.AcquisitionCommands.X_Y_DISPLAY, "ON" if enabled else "OFF")

    def get_x_y_display(self) -> bool:
        return "ON" in self._transmit(self.AcquisitionCommands.X_Y_DISPLAY)

    def get_vdiv(self) -> float:
        response = (
            str(self._transmit(self.AcquisitionCommands.VDIV))
            .split(" ")[1]
            .split("V")[0]
        )
        return float(response)

    def get_offset(self) -> float:
        response = float(
            str(self._transmit(self.AcquisitionCommands.OFFSET))
            .split(" ")[1]
            .split("V")[0]
        )
        return response

    def get_tdiv(self) -> float:
        response = float(
            str(self._transmit(self.AcquisitionCommands.TDIV))
            .split(" ")[1]
            .split("S")[0]
        )
        return response

    def get_sample_rate(self) -> float:
        response = float(
            str(self._transmit(self.AcquisitionCommands.SAMPLE_RATE))
            .split(" ")[1]
            .split("S")[0]
        )
        return response

    def get_sample_points(self) -> float:
        response = float(
            str(
                self._transmit(
                    self.AcquisitionCommands.NUMBER_OF_ACQUIRED_SAMPLES, "C1"
                )
            )
            .split(" ")[1]
            .split("pts")[0]
        )
        return response

    def get_screen_dump(self) -> bool:
        times = []
        volts = []
        vdiv = self.get_vdiv()
        offset = self.get_offset()
        tdiv = self.get_tdiv()
        sara = self.get_sample_rate()
        num_samples = self.get_sample_points()

        a = Quantity(vdiv, units="V")
        b = Quantity(offset, units="V")
        c = Quantity(tdiv, units="S")

        print(f"vdiv: {a}")
        print(f"offset: {b}")
        print(f"tdiv: {c}")
        print(f"sara: {sara}")
        print(f"numsamples: {num_samples}")

        self._write(self.AcquisitionCommands.WAVEFORM, params="dat2", query=True)
        response = self._read(20000)
        values = list(response)
        values.pop()
        values.pop()

        # hdiv = 14
        # vdiv = 8

        insert = len(values) / num_samples
        time_interval = 1 / sara / insert
        start_time = -(tdiv * 14 / 2)

        for value in values:
            value = value - 256 if value > 127 else value
            volts.append(value * (vdiv / 25) - offset)
            start_time += time_interval
            times.append(start_time)

        plt.plot(times, volts)
        plt.grid()
        plt.show()
        print("blah")
        return response


class Siglent1104X_107(Siglent1104X):
    IP_ADDRESS = "192.168.1.107"
