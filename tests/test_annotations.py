from flyecho.annotations import FlyWireAnnotations


def test_flywire_annotation_loader_and_search(tmp_path):
    path = tmp_path / "annotations.tsv"
    path.write_text(
        "root_id\tcell_type\tcell_class\tsuper_class\tflow\n"
        "101\tLC4\toptic\tvisual_projection\tafferent\n"
        "102\tLPLC2\toptic\tvisual_projection\tafferent\n"
        "103\tGF\tdescending\tcentral\tefferent\n",
        encoding="utf-8",
    )

    annotations = FlyWireAnnotations.from_path(path)
    assert annotations.summary() == {
        "annotations": 3,
        "typed_neurons": 3,
        "unique_cell_types": 3,
    }
    assert annotations.get(103).cell_type == "GF"
    assert annotations.root_ids_for_type("LC4") == [101]
    assert [row.root_id for row in annotations.search("visual_projection")] == [101, 102]
