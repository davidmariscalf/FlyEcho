from pathlib import Path

from flyecho.connectome import FlyWireEdgeList


def test_edge_loader_and_local_queries(tmp_path: Path):
    p = tmp_path / "edges.csv"
    p.write_text(
        "pre_root_id,post_root_id,syn_count\n"
        "1,2,7\n"
        "1,3,2\n"
        "2,3,4\n"
        "3,4,9\n",
        encoding="utf-8",
    )
    graph = FlyWireEdgeList.from_csv(p, min_weight=3)
    s = graph.summary()
    assert s["neurons"] == 4
    assert s["edges"] == 3
    assert graph.strongest_outgoing(1)[0].post == 2
    assert graph.strongest_incoming(3)[0].pre == 2
    assert graph.neighbors(3) == {2, 4}


def test_subgraph_and_hubs(tmp_path: Path):
    p = tmp_path / "edges.tsv"
    p.write_text(
        "pre\tpost\tweight\n"
        "1\t2\t8\n"
        "2\t3\t7\n"
        "3\t4\t6\n"
        "10\t11\t20\n",
        encoding="utf-8",
    )
    graph = FlyWireEdgeList.from_csv(p)
    ego = graph.ego_subgraph([1], hops=2)
    assert ego.summary()["neurons"] == 3
    assert ego.summary()["edges"] == 2
    assert graph.hubs(limit=1)[0][0] in {10, 11}
