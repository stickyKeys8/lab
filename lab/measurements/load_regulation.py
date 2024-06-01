"""Testscript to test my Instruments."""
import datetime
import logging
import pathlib
import socket
import time

import pandas
import pyvisa

from lab.instruments.scpi_instrument import SCPIInstrument
from lab.instruments.rigol_dl_3021_a import RigolDL3021A_247 as Load
from lab.instruments.rohde_und_schwarz_hmc8012 import RohdeUndSchwarzHMC8012_146 as Multimeter
from lab.instruments.siglent_spd_1305_x import Siglent1305X_249 as PowerSupply

# pylint: disable=line-too-long
# pylint: disable=too-many-locals
# pylint: disable=broad-exception-caught
# pylint: disable=broad-exception-raised

TIMEOUT = 5.0
RESULTS_PATH = pathlib.Path(__file__).parent
VERSION = "1.0.0"
PSU_SETTLING_TIME_S = 1.5

def run() -> pandas.DataFrame:
    """Run a load regulation measurement."""
    logger = logging.getLogger(__name__)

    resource_manager = pyvisa.ResourceManager()
    load_connection = resource_manager.open_resource(Load.TCPIP_INSTRUMENT_STRING, open_timeout=TIMEOUT)
    load = Load(load_connection)

    dmm_connection = create_socket_and_connect(Multimeter.IP_ADDRESS, Multimeter.PORT)
    dmm = Multimeter(dmm_connection)

    psu_connection = create_socket_and_connect(PowerSupply.IP_ADDRESS, PowerSupply.PORT)
    psu = PowerSupply(psu_connection)

    connections :list[socket.socket | pyvisa.resources.TCPIPInstrument] = [load_connection, dmm_connection, psu_connection]
    instruments : list[SCPIInstrument] = [load, dmm, psu]

    time_stamp = datetime.datetime.now()
    meta_df = pandas.DataFrame(columns=["meta"])
    meta_df.loc["Script"] = pathlib.Path(__file__).name
    meta_df.loc["Timestamp"] = str(time_stamp)
    meta_df.loc["Instruments"] = " ".join([instrument.get_id_string() for instrument in instruments])
    meta_df.loc["Version"] = VERSION
    meta_df.loc["DUT"] = "LM2596"

    results_df = pandas.DataFrame(columns=["load_current", "output_voltage"])

    try:
        for value in meta_df["meta"]:
            logger.info(value)

        psu.set_voltage(1.234)
        psu.set_current(1.234)
        psu.set_mode("4W")
        psu.set_enable_wave_display(True)
        psu.set_enable_output(True)

        time.sleep(PSU_SETTLING_TIME_S)

        log_psu_state(logger, psu)

        

        load_currents = [x / 10.0 for x in range(0, 31, 1)]
        voltages = [x / 10.0 for x in range(0, 31, 1)]
        results_df['load_current'] = load_currents
        results_df['output_voltage'] = voltages

        time_stamp_for_filename = time_stamp.strftime("%Y%m%d_%H%M%S") # pylint: disable=unused-variable
        file_name = "load_regulation.csv"

        results_df.to_csv(RESULTS_PATH / file_name, header=["load_current", "output_voltage"])
        meta_df.to_csv((RESULTS_PATH / file_name).with_suffix(".meta.csv"), header=["meta"])

        return results_df
    except Exception as ex:
        logger.exception(ex)
        raise Exception from ex
    finally:
        psu.set_enable_output(False)
        psu.set_enable_wave_display(False)
        psu.set_mode("2W")
        for connection in connections:
            connection.close()

def create_socket_and_connect(ip_address: str, port: int):
    """Create a network socket and connect to it."""
    new_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    new_socket.settimeout(TIMEOUT)
    new_socket.connect((ip_address, port))
    return new_socket

def log_psu_state(logger, psu):
    logger.info("PSU output is: %s", 'on' if psu.get_output_enabled() else 'off')
    logger.info("PSU wave display is: %s", 'on' if psu.get_wave_display_enabled() else 'off')
    logger.info("PSU mode is: %s",'4W' if psu.get_4w_mode_enabled() else '2W')
    logger.info("PSU set voltage: %f", psu.get_voltage())
    logger.info("PSU measured voltage: %f", psu.measure_voltage())
    logger.info("PSU set current: %f", psu.get_current())
    logger.info("PSU measured current: %f", psu.measure_current())
    logger.info("PSU measured power: %f", psu.measure_power())

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run()
