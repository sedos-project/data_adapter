from data_adapter import collection


def test_get_artifacts_from_collection():
    artifacts = collection.get_artifacts_from_collection("test_collection")
    assert len(artifacts) == 6
    artifacts = collection.get_artifacts_from_collection(
        "test_collection", "net capacity factor"
    )
    assert len(artifacts) == 1
