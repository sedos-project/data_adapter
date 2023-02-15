from data_adapter import collection


def test_get_artifacts_from_collection():
    artifacts = collection.get_artifacts_from_collection("simple")
    assert len(artifacts) == 6
    artifacts = collection.get_artifacts_from_collection("simple", "net capacity factor")
    assert len(artifacts) == 1
