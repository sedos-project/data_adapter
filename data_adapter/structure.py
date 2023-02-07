from __future__ import annotations

from collections import defaultdict, namedtuple

import sqlalchemy as sa
from sqlalchemy.orm import declarative_base, relationship

from data_adapter import settings


class StructureError(Exception):
    """Raised if structure is corrupted"""


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
    inputs: InputOutput = relationship(
        "InputOutput", secondary=parameter_inputs, backref="to_parameters"
    )
    outputs: InputOutput = relationship(
        "InputOutput", secondary=parameter_outputs, backref="from_parameters"
    )


class InputOutput(Base):
    __tablename__ = "input_output"

    id = sa.Column(sa.Integer, primary_key=True)  # noqa: A003
    name = sa.Column(sa.String)


HARDCODED_ES_STRUCTURE = {
    "energy transformation unit": {
        "input_ratio": {"inputs": ["gas"], "outputs": ["electricity"]},
        "output_ratio": {"inputs": ["gas"], "outputs": ["electricity"]},
        "emission_factor": {"inputs": ["gas"], "outputs": ["co2"]},
    },
    "battery storage": {
        "input_ratio": {"inputs": ["electricity"], "outputs": ["electricity"]},
        "output_ratio": {"inputs": ["electricity"], "outputs": ["electricity"]},
        "e2p_ratio": {"inputs": ["electricity"], "outputs": []},
    },
}

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


def get_energy_structure():
    return HARDCODED_ES_STRUCTURE


def get_processes():
    return list(HARDCODED_ES_STRUCTURE)


def init_database():
    Base.metadata.create_all(settings.engine)
