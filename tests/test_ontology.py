from data_adapter import ontology


def test_multiple_subject_entries():
    metadata = {"name": "meta_name", "subject": [{"name": "test"}, {"name": "test2"}]}
    assert ontology.get_subject(metadata) == "test_test2"


def test_check_annotations():
    metadata_no_subject = {
        "name": "metadata with no subject",
        "resources": [{"schema": {"fields": []}}],
    }
    checks = list(ontology.check_annotations_in_metadata(metadata_no_subject))
    assert len(checks) == 1
    assert checks[0].quality == ontology.AnnotationQuality.NoAnnotation

    metadata_with_name_subject = {
        "name": "metadata with subject",
        "subject": [{"name": "subject"}],
        "resources": [{"schema": {"fields": []}}],
    }
    checks = list(ontology.check_annotations_in_metadata(metadata_with_name_subject))
    assert len(checks) == 1
    assert checks[0].quality == ontology.AnnotationQuality.NameAnnotation

    metadata_with_mixed_subject = {
        "name": "metadata with subject",
        "subject": [{"name": "subject"}, {}],
        "resources": [{"schema": {"fields": []}}],
    }
    checks = list(ontology.check_annotations_in_metadata(metadata_with_mixed_subject))
    assert len(checks) == 1
    assert checks[0].quality == ontology.AnnotationQuality.NoAnnotation

    metadata_with_multiple_fields = {
        "name": "metadata with subject",
        "subject": [{"name": "subject"}, {}],
        "resources": [
            {
                "schema": {
                    "fields": [
                        {"name": "no"},
                        {"name": "mixed", "isAbout": [{"name": "mix1"}, {}]},
                        {
                            "name": "mixedname",
                            "isAbout": [
                                {"name": "name1"},
                                {"name": "name2", "path": "oeo"},
                            ],
                        },
                        {
                            "name": "name",
                            "isAbout": [{"name": "name1"}, {"name": "name2"}],
                        },
                        {
                            "name": "name",
                            "isAbout": [
                                {"name": "name1", "path": "oeo"},
                                {"name": "name2", "path": "oeo"},
                            ],
                        },
                    ]
                }
            }
        ],
    }
    checks = list(ontology.check_annotations_in_metadata(metadata_with_multiple_fields))
    assert len(checks) == 6
    assert checks[0].field == "subject"
    assert checks[0].quality == ontology.AnnotationQuality.NoAnnotation
    assert checks[1].field == "no"
    assert checks[1].quality == ontology.AnnotationQuality.NoAnnotation
    assert checks[2].field == "mixed"
    assert checks[2].quality == ontology.AnnotationQuality.NoAnnotation
    assert checks[3].field == "mixedname"
    assert checks[3].quality == ontology.AnnotationQuality.NameAnnotation
    assert checks[4].field == "name"
    assert checks[4].quality == ontology.AnnotationQuality.NameAnnotation
    # assert checks[5].field == "oeo"
    # assert checks[5].quality == ontology.AnnotationQuality.OEOAnnotation
