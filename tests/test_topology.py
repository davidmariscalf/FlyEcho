import json

from flyecho.topology import edge_weight, topology_dot, topology_json, validate_topology


def test_topology_is_valid_and_exportable():
    validate_topology()
    assert edge_weight("LC4-like", "GF-like") > 0
    assert edge_weight("GF-like", "TTMn-like") > 0

    payload = json.loads(topology_json())
    assert len(payload["nodes"]) == 6
    assert len(payload["edges"]) == 5
    assert "GF-like" in topology_dot()


def test_unknown_edge_is_rejected():
    try:
        edge_weight("missing", "GF-like")
    except KeyError:
        pass
    else:
        raise AssertionError("unknown edge should raise KeyError")
