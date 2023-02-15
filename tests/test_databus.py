import pathlib
import tempfile

from data_adapter import databus

EXAMPLE_ARTIFACT = "https://energy.databus.dbpedia.org/felixmaur/modex/modex_tech_photovoltaics_rooftop"  # noqa: E501
EXAMPLE_COLLECTION = "https://energy.databus.dbpedia.org/felixmaur/collections/modex_test_renewable"
CSV_ARTIFACT = "https://energy.databus.dbpedia.org/felixmaur/modex/modex_tech_photovoltaics_rooftop/v1/modex_tech_photovoltaics_rooftop_type=data.csv"  # noqa: E501


def test_version():
    version = databus.get_latest_version_of_artifact(EXAMPLE_ARTIFACT)
    assert version == "v3"


def test_collections():
    artifacts = databus.get_artifacts_from_collection(EXAMPLE_COLLECTION)
    assert len(artifacts) == 11


def test_artifact_file():
    databus_files = databus.get_artifact_filenames(EXAMPLE_ARTIFACT, "v1")
    assert len(databus_files) == 2
    assert (
        "https://energy.databus.dbpedia.org/felixmaur/modex/modex_tech_photovoltaics_rooftop/v1/modex_tech_photovoltaics_rooftop_type=data.csv"  # noqa: E501
        in databus_files
    )
    assert (
        "https://energy.databus.dbpedia.org/felixmaur/modex/modex_tech_photovoltaics_rooftop/v1/modex_tech_photovoltaics_rooftop_type=metadata.json"  # noqa: E501
        in databus_files
    )


def test_download_csv():
    test_filename = "test.csv"
    with tempfile.TemporaryDirectory() as tmpdirname:
        csv_filename = pathlib.Path(tmpdirname) / test_filename
        assert not csv_filename.exists()
        databus.download_artifact(CSV_ARTIFACT, csv_filename)
        assert csv_filename.exists()
