from data_adapter import collection
from tests import utils


def test_get_artifacts_from_collection():
    artifacts = collection.get_artifacts_from_collection("simple")
    assert len(artifacts) == 6


def test_filter_process_from_collection():
    artifacts = collection.get_artifacts_from_collection("simple", "modex_capacity_factor")
    assert len(artifacts) == 1


def test_filter_process_from_collection_with_annotations():
    with utils.turn_on_annotations():
        artifacts = collection.get_artifacts_from_collection("simple", "net capacity factor")
    assert len(artifacts) == 1
