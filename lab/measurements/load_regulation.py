"""Testscript to test my Instruments."""
import datetime
import logging
import pathlib
import socket
import time

import pandas
import pyvisa

from lab.instruments.rigol_dl_3021_a import RigolDL3021A_247 as Load
from lab.instruments.rohde_und_schwarz_hmc8012 import \
    RohdeUndSchwarzHMC8012_146 as Multimeter
from lab.instruments.scpi_instrument import SCPIInstrument
from lab.instruments.siglent_spd_1305_x import Siglent1305X_249 as PowerSupply

# pylint: disable=line-too-long
# pylint: disable=too-many-locals
# pylint: disable=broad-exception-caught
# pylint: disable=broad-exception-raised

TIMEOUT = 1000
RESULTS_PATH = pathlib.Path(__file__).parent
VERSION = "1.0.0"
PSU_SETTLING_TIME_S = 1.5
LOAD_SETTLING_TIME_S = .2

def run() -> pandas.DataFrame:
    """Run a load regulation measurement."""
    logger = logging.getLogger(__name__)

    resource_manager = pyvisa.ResourceManager()
    load_connection = resource_manager.open_resource(Load.TCPIP_INSTRUMENT_STRING)
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

    result_header = ["psu_measured_voltages", "psu_measured_currents", "psu_measured_powers", "load_measured_voltages", "load_measured_currents", "load_measured_powers"]
    results_df = pandas.DataFrame(columns=result_header)

    try:
        for value in meta_df["meta"]:
            logger.info(value)

        psu.set_voltage(6)
        psu.set_current(5)
        psu.set_mode("4W")
        psu.set_enable_output(True)

        time.sleep(PSU_SETTLING_TIME_S)

        log_psu_state(logger, psu)

        logger.info("Load measured voltage: %f",load.measure_voltage())
        logger.info("Load measured current: %f",load.measure_current())
        logger.info("Load measured power: %f",load.measure_power())

        load_currents = [x / 100.0 for x in range(0, 201, 1)]

        psu_measured_voltages = []
        psu_measured_currents = []
        psu_measured_powers = []

        load_measured_voltages = []
        load_measured_currents = []
        load_measured_powers = []

        load.set_enable_input(True)

        for load_current in load_currents:
            load.set_current(load_current)
            time.sleep(LOAD_SETTLING_TIME_S)

            psu_measured_voltages.append(psu.measure_voltage())
            psu_measured_currents.append(psu.measure_current())
            psu_measured_powers.append(psu.measure_power())

            load_measured_voltages.append(load.measure_voltage())
            load_measured_currents.append(load.measure_current())
            load_measured_powers.append(load.measure_power())

        results_df['psu_measured_voltages'] = psu_measured_voltages
        results_df['psu_measured_currents'] = psu_measured_currents
        results_df['psu_measured_powers'] = psu_measured_powers

        results_df['load_measured_voltages'] = load_measured_voltages
        results_df['load_measured_currents'] = load_measured_currents
        results_df['load_measured_powers'] = load_measured_powers

        time_stamp_for_filename = time_stamp.strftime("%Y%m%d_%H%M%S") # pylint: disable=unused-variable
        file_name = "load_regulation.csv"

        results_df.to_csv(RESULTS_PATH / file_name, header=result_header)
        meta_df.to_csv((RESULTS_PATH / file_name).with_suffix(".meta.csv"), header=["meta"])

        return results_df
    except Exception as ex:
        logger.exception(ex)
        raise Exception from ex
    finally:
        load.set_enable_input(False)
        psu.set_enable_output(False)
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
