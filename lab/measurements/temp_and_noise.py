"""Testscript to test my Instruments."""

# pylint: disable=line-too-long
# pylint: disable=too-many-locals 
# pylint: disable=broad-exception-caught
# pylint: disable=broad-exception-raised
# pylint: disable=unused-variable

import datetime
import logging
import pathlib
import socket
import time

import pandas

from lab.instruments.scpi_instrument import SCPIInstrument
from lab.instruments.rigol_dl_3021_a import RigolDL3021A_247 as Load
from lab.instruments.rohde_und_schwarz_hmc8012 import RohdeUndSchwarzHMC8012_146 as Multimeter
from lab.instruments.siglent_sds_1104_x import Siglent1104X_107 as Oscilloscope
from lab.instruments.siglent_spd_1305_x import Siglent1305X_249 as PowerSupply


def run() -> pandas.DataFrame:
    """Run a load regulation measurement."""

    load_connection = create_socket_and_connect(Load.IP_ADDRESS, Load.PORT)
    psu_connection = create_socket_and_connect(PowerSupply.IP_ADDRESS, PowerSupply.PORT)
    scope_connection = create_socket_and_connect(Oscilloscope.IP_ADDRESS, Oscilloscope.PORT)
    dmm_connection = create_socket_and_connect(Multimeter.IP_ADDRESS, Multimeter.PORT)
    connections: list[socket.socket] = [
        load_connection,
        psu_connection,
        scope_connection,
        dmm_connection,
    ]

    load = Load(load_connection)
    psu = PowerSupply(psu_connection)
    scope = Oscilloscope(scope_connection)
    dmm = Multimeter(dmm_connection)
    instruments: list[SCPIInstrument] = [load, psu, scope, dmm]

    logger = logging.getLogger(__name__)

    load_sweep_df = pandas.DataFrame(columns=["results"])
    line_sweep_df = pandas.DataFrame(columns=["results"])
    meta_df = pandas.DataFrame(columns=["meta"])

    load_currents = [x / 100.0 for x in range(0, 201, 1)]
    line_voltages = list(range(10,26,1))
    results_path = pathlib.Path(__file__).parent

    meta_df.loc["Script"] = pathlib.Path(__file__).name
    meta_df.loc["Timestamp"] = datetime.datetime.now().strftime("%d_%m_%Y_%H_%M_%S")
    meta_df.loc["Instruments"] = " ".join([instrument.get_id_string() for instrument in instruments])
    meta_df.loc["Version"] = "1.0.0"
    meta_df.loc["DUT"] = "LM2596_2 protoboard with 1N5817 diode and 330uH not shielded inductor plus 33uF output cap"
    meta_df.loc["Set input voltage"] = 23
    meta_df.loc["Set output voltage"] = 12
    meta_df.loc["Set input current"] = 5
    meta_df.loc["PSU sense"] = "2W"
    meta_df.loc["File name prefix"] = "lr.csv"
    meta_df.loc["Load settling time"] = 2
    meta_df.loc["load currents"] = " ".join([str(current) for current in load_currents])

    psu_measured_voltages = []
    psu_measured_currents = []
    psu_measured_powers = []
    load_measured_voltages = []
    load_measured_currents = []
    load_measured_powers = []
    temperatures = []
    load_measured_line_voltages = []
    psu_measured_line_voltages = []

    try:
        for value in meta_df["meta"]:
            logger.info(value)

        psu.set_voltage(10)
        psu.set_current(5)
        psu.set_mode(meta_df["meta"]["PSU sense"])
        psu.set_enable_output(True)

        # Line sweep
        for line_voltage in line_voltages:
            psu.set_voltage(line_voltage)
            time.sleep(2)
            load_measured_line_voltages.append(load.measure_voltage())
            psu_measured_line_voltages.append(psu.measure_voltage())

        psu.set_voltage(meta_df["meta"]["Set input voltage"])
        psu.set_current(meta_df["meta"]["Set input current"])
        psu.set_mode(meta_df["meta"]["PSU sense"])
        load.set_enable_input(True)

        # Load sweep
        for load_current in load_currents:
            load.set_current(load_current)
            time.sleep(meta_df["meta"]["Load settling time"])
            psu_measured_voltages.append(psu.measure_voltage())
            psu_measured_currents.append(psu.measure_current())
            psu_measured_powers.append(psu.measure_power())
            load_measured_voltages.append(load.measure_voltage())
            load_measured_currents.append(load.measure_current())
            load_measured_powers.append(load.measure_power())
            temperatures.append(dmm.fetch())

        line_sweep_df["psu_measured_line_voltages"] = psu_measured_line_voltages
        line_sweep_df["load_measured_line_voltages"] = load_measured_line_voltages
        
        load_sweep_df["psu_measured_voltages"] = psu_measured_voltages
        load_sweep_df["psu_measured_currents"] = psu_measured_currents
        load_sweep_df["psu_measured_powers"] = psu_measured_powers
        load_sweep_df["load_measured_voltages"] = load_measured_voltages
        load_sweep_df["load_measured_currents"] = load_measured_currents
        load_sweep_df["load_measured_powers"] = load_measured_powers
        load_sweep_df["temperatures"] = temperatures

        load_sweep_df.to_csv(results_path / (meta_df["meta"]["Timestamp"] + "_load_sweep_" +  meta_df["meta"]["File name prefix"]), header=load_sweep_df.columns)
        line_sweep_df.to_csv(results_path / (meta_df["meta"]["Timestamp"] + "_line_sweep_" +  meta_df["meta"]["File name prefix"]), header=line_sweep_df.columns)
        meta_df.to_csv((results_path / (meta_df["meta"]["Timestamp"] + "_" + meta_df["meta"]["File name prefix"])).with_suffix(".meta.csv"), header=meta_df.columns)

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
    new_socket.connect((ip_address, port))
    return new_socket

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run()
