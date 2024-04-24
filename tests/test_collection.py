from data_adapter import collection
from tests import utils


def test_get_artifacts_from_collection():
    artifacts = collection.get_artifacts_from_collection("simple")
    assert len(artifacts) == 6


def test_get_artifact_from_collection():
    artifact = collection.get_artifact_from_collection("simple", "modex", "modex_tech_generator_gas", "v2")
    artifact_latest = collection.get_artifact_from_collection("simple", "modex", "modex_tech_generator_gas")
    assert artifact.datatype == 0
    assert artifact == artifact_latest


def test_get_processes_from_collection():
    processes = collection.get_processes_from_collection("subprocesses")
    assert len(processes) == 7


def test_filter_process_from_collection():
    artifacts = collection.get_artifacts_from_collection("simple", "modex_capacity_factor")
    assert len(artifacts) == 1


def test_filter_process_from_collection_with_annotations():
    with utils.turn_on_annotations():
        artifacts = collection.get_artifacts_from_collection("simple", "net capacity factor")
    assert len(artifacts) == 1


def test_infer_collection_metadata():
    collection_name = "subprocesses"
    metadata = collection.get_collection_meta(collection_name)
    collection.infer_collection_metadata(collection_name, metadata)
    wind_turbine = metadata["artifacts"]["modex"]["modex_tech_wind_turbine"]
    assert len(wind_turbine["names"]) == 3
    assert "modex_tech_wind_turbine_onshore" in wind_turbine["names"]
    assert "wind_onshore" in wind_turbine["names"]
    assert "wind_offshore" in wind_turbine["names"]
    assert len(wind_turbine["subjects"]) == 3
    assert "onshore wind farm" in wind_turbine["subjects"]
    assert "Wind Onshore" in wind_turbine["subjects"]
    assert "Wind Offshore" in wind_turbine["subjects"]
