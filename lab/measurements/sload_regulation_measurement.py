"""Testscript to test my Instruments."""

import socket

from quantiphy import Quantity

from lab.instruments.rohde_und_schwarz_hmc8012 import (
    RohdeUndSchwarzHMC8012_146 as Multimeter,
)
from lab.instruments.siglent_sds_1104_x import Siglent1104X_107 as Oscilloscope
from lab.instruments.siglent_spd_1305_x import Siglent1305X_249 as PowerSupply

TIMEOUT = 30.0


def run():
    """Run a load regulation measurement."""
    dmm_socket = create_socket_and_connect(Multimeter.IP_ADDRESS, Multimeter.PORT)
    dmm = Multimeter(dmm_socket)

    scope_socket = create_socket_and_connect(Oscilloscope.IP_ADDRESS, Oscilloscope.PORT)
    scope = Oscilloscope(scope_socket)

    psu_socket = create_socket_and_connect(PowerSupply.IP_ADDRESS, PowerSupply.PORT)
    psu = PowerSupply(psu_socket)

    try:
        print(dmm.get_id_string())
        print(scope.get_id_string())
        print(psu.get_id_string())
        screenshot = scope.get_screen_dump()
        print(Quantity(dmm.fetch(), "V").fixed(strip_zeros=False))
        print(Quantity(dmm.read(), "V").fixed(strip_zeros=False))
        print(dmm.get_trigger_mode())
        dmm.set_trigger_mode("SING")
        dmm.wait_until_operation_is_completed()
        print(dmm.get_trigger_mode())
        scope.run()
        scope.set_x_y_display(True)
        scope.wait_until_operation_is_completed()
        response = Quantity(dmm.measure_voltage_dc("AUTO"), "V")
        print(response.fixed(strip_zeros=False))
        print(scope.get_x_y_display())
        print(scope.get_sample_status())
        scope.set_x_y_display(False)
        scope.wait_until_operation_is_completed()
        scope.stop()
    except Exception as ex:  # pylint: disable=broad-exception-caught
        print(ex)
    finally:
        dmm_socket.close()
        scope_socket.close()
        psu_socket.close()


def create_socket_and_connect(ip_address: str, port: int):
    """Create a network socket and connect to it."""
    new_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    new_socket.settimeout(TIMEOUT)
    new_socket.connect((ip_address, port))
    return new_socket


if __name__ == "__main__":
    run()
