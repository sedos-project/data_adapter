from __future__ import annotations

import json
from collections import defaultdict, namedtuple

import re
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


def check_character_convention(dataframe=None):
    """
    Check in parameter-, process-, input-and output-column for character convention.

    Parameters
    ----------
    dataframe

    """
    for col in dataframe.columns[1:]:
        for element in dataframe[col]:
            if not IDENTIFIER_PATTERN.match(element):
                raise ValueError(
                    f"Wrong syntax: {element}\nAllowed are characters: a-z and 0-9 and , and _"
                )


def get_energy_structure(process_parameter_path: str = None) -> dict:
    """
    Parse processes and its parameters with corresponding inputs and outputs to dict.

    Parameters
    ----------
    parameter_process_path: str
        Path to process and parameter sheet.

    Returns
    -------
    ValueError
        if processes of parameters do not match character convention
    ES_STRUCTURE: dict
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

    ES_STRUCTURE = {}

    for dic in list_dic:

        dic_para = {}
        dic_para[dic.get("parameter")] = dict(
            inputs=dic.get("inputs").replace(" ", "").split(",")
        ) | dict(outputs=dic.get("outputs").replace(" ", "").split(","))

        if dic.get("process") not in ES_STRUCTURE:
            ES_STRUCTURE[dic.get("process")] = dic_para
        else:
            ES_STRUCTURE[dic.get("process")] = (
                ES_STRUCTURE[dic.get("process")] | dic_para
            )

    return ES_STRUCTURE


def get_processes():
    return list(HARDCODED_ES_STRUCTURE)


def init_database():
    Base.metadata.create_all(settings.engine)
