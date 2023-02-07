from collections import defaultdict, namedtuple
from data_adapter.databus import download_collection

from pathlib import Path
import json

import sqlalchemy as sa
from sqlalchemy.orm import declarative_base, relationship

from data_adapter import settings



class StructureError(Exception):
    """Raised if structure is corrupted"""


this_path = Path(__file__).parent.parent /"collections"/"hack-a-thon"

with open(this_path / "HARDCODED_ES_STRUCT.json", "r") as f:
    HARDCODED_ES_STRUCTURE = json.load(f)


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
    parameters = relationship("Parameter")


class Parameter(Base):
    __tablename__ = "parameter"

    id = sa.Column(sa.Integer, primary_key=True)  # noqa: A003
    process_id = sa.Column(sa.BIGINT, sa.ForeignKey("process.id"), nullable=False)
    name = sa.Column(sa.String)
    inputs = relationship(
        "InputOutput", secondary=parameter_inputs, backref="to_parameters"
    )
    outputs = relationship(
        "InputOutput", secondary=parameter_outputs, backref="from_parameters"
    )


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


def get_energy_structure():
    return HARDCODED_ES_STRUCTURE


def get_processes():
    return list(HARDCODED_ES_STRUCTURE)




def init_database():
    Base.metadata.create_all(settings.engine)

