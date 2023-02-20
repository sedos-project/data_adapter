from __future__ import annotations

import json
from collections import defaultdict, namedtuple

import re
from collections import defaultdict, namedtuple
from pathlib import Path

import pandas as pd
import sqlalchemy as sa
from sqlalchemy.orm import declarative_base, relationship

from data_adapter import settings

# constants
MAX_IDENTIFIER_LENGTH = 50
# pylint:disable=C0209
IDENTIFIER_PATTERN = re.compile(
    "^[a-z][a-z0-9_, ]{0,%s}$" % (MAX_IDENTIFIER_LENGTH - 1)
)


class StructureError(Exception):
    """Raised if structure is corrupted"""


with open(settings.STRUCTURES_DIR / "HARDCODED_ES_STRUCT.json", "r") as hardcoded_es_file:
    HARDCODED_ES_STRUCTURE = json.load(hardcoded_es_file)


Base = declarative_base()

parameter_inputs = sa.Table(
    "parameter_inputs",
    Base.metadata,
    sa.Column("parameter_id", sa.ForeignKey("parameter.id"), primary_key=True),
    sa.Column("input_id", sa.ForeignKey("input_output.id"), primary_key=True),
)

parameter_outputs = sa.Table(
    "parameter_outputs",
    Base.metadata,
    sa.Column("parameter_id", sa.ForeignKey("parameter.id"), primary_key=True),
    sa.Column("output_id", sa.ForeignKey("input_output.id"), primary_key=True),
)


class Process(Base):
    __tablename__ = "process"

    id = sa.Column(sa.Integer, primary_key=True)  # noqa: A003
    name = sa.Column(sa.String)
    parameters: Parameter = relationship("Parameter")


class Parameter(Base):
    __tablename__ = "parameter"

    id = sa.Column(sa.Integer, primary_key=True)  # noqa: A003
    process_id = sa.Column(sa.BIGINT, sa.ForeignKey("process.id"), nullable=False)
    name = sa.Column(sa.String)
    inputs: InputOutput = relationship("InputOutput", secondary=parameter_inputs, backref="to_parameters")
    outputs: InputOutput = relationship("InputOutput", secondary=parameter_outputs, backref="from_parameters")


class InputOutput(Base):
    __tablename__ = "input_output"

    id = sa.Column(sa.Integer, primary_key=True)  # noqa: A003
    name = sa.Column(sa.String)


AdditionalParameter = namedtuple("AdditionalParameter", ("subject", "isAbout"))

ADDITONAL_PARAMETERS = {
    "onshore wind farm": [
        AdditionalParameter("net capacity factor", "onshore"),
    ]
}


def get_additional_parameters(process: str):
    if process not in ADDITONAL_PARAMETERS:
        return {}
    parameters = defaultdict(list)
    for parameter in ADDITONAL_PARAMETERS[process]:
        parameters[parameter.subject].append(parameter.isAbout)
    return parameters


def check_character_convention(dataframe: pd.DataFrame):
    """
    Check in parameter-, process-, input-and output-column for character convention.

    Parameters
    ----------
    dataframe: pandas.DataFrame
        Parameters in dataframe are checked for convention

    Raises
    ------
    ValueError
        if element in dataframe does not fit character convention

    """
    for col in dataframe.columns[1:]:
        for element in dataframe[col]:
            if not isinstance(element, str):
                continue
            if not IDENTIFIER_PATTERN.match(element):
                raise ValueError(
                    f"Wrong syntax: {element}\nAllowed are characters: a-z and 0-9 and , and _"
                )


def get_energy_structure(process_parameter_path: str) -> dict:
    """
    Parse processes and its parameters with corresponding inputs and outputs to dict.

    Parameters
    ----------
    process_parameter_path: str
        Path to process and parameter sheet.

    Returns
    -------
    dict
        Energy modelling processes, its parameters and inputs and output
    """

    process_parameter_in_out = pd.read_csv(
        filepath_or_buffer=process_parameter_path,
        delimiter=";",
        encoding="utf-8",
        usecols=["parameter", "process", "inputs", "outputs"],
    )
    check_character_convention(process_parameter_in_out)

    # create ES_STRUCTURE dict from process_parameter_in_out
    list_dic = process_parameter_in_out.to_dict(orient="records")

    es_structure = {}

    for dic in list_dic:
        dic_para = {}

        if isinstance(dic.get("inputs"), str):
            inputs = {"inputs": dic.get("inputs").replace(" ", "").split(",")}
        else:
            inputs = {"inputs": []}
        if isinstance(dic.get("outputs"), str):
            outputs = {"outputs": dic.get("outputs").replace(" ", "").split(",")}
        else:
            outputs = {"outputs": []}

        dic_para[dic.get("parameter")] = inputs | outputs

        if dic.get("process") not in es_structure:
            es_structure[dic.get("process")] = dic_para
        else:
            es_structure[dic.get("process")] = (
                es_structure[dic.get("process")] | dic_para
            )

    return es_structure


def get_processes():
    return list(HARDCODED_ES_STRUCTURE)


def init_database():
    Base.metadata.create_all(settings.engine)
