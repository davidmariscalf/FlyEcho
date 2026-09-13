from pathlib import Path
from flyecho.connectome import FlyWireEdgeList


def test_edge_loader(tmp_path: Path):
    p = tmp_path / "edges.csv"
    p.write_text(
        "pre_root_id,post_root_id,syn_count\n"
        "1,2,7\n"
        "1,3,2\n"
        "2,3,4\n",
        encoding="utf-8",
    )
    graph = FlyWireEdgeList.from_csv(p, min_weight=3)
    s = graph.summary()
    assert s["neurons"] == 3
    assert s["edges"] == 2
    assert graph.strongest_outgoing(1)[0].post == 2
