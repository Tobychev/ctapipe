import json

import pytest

from ctapipe.core import Provenance
from ctapipe.core.provenance import _ActivityProvenance


@pytest.fixture
def provenance(monkeypatch):
    # the singleton nature of Provenance messes with
    # the order-independence of the tests asserting
    # the provenance contains the correct information
    # so we monkeypatch back to an empty state here
    prov = Provenance()
    monkeypatch.setattr(prov, "_activities", [])
    monkeypatch.setattr(prov, "_finished_activities", [])

    prov.start_activity("test1")
    prov.add_input_file("input.txt")
    prov.add_output_file("output.txt")
    prov.start_activity("test2")
    prov.add_input_file("input_a.txt")
    prov.add_input_file("input_b.txt")
    prov.finish_activity("test2")
    prov.finish_activity("test1")
    return prov


def test_provenance_activity_names(provenance):
    assert set(provenance.finished_activity_names) == {"test2", "test1"}


def test_ActivityProvenance():
    prov = _ActivityProvenance()
    prov.start()
    prov.register_input("test.txt")
    prov.register_input("test2.txt")
    prov.register_output("out.txt")
    prov.sample_cpu_and_memory()
    prov.finish()


def test_provenence_contextmanager():

    prov = Provenance()

    with prov.activity("myactivity"):
        assert "myactivity" in prov.active_activity_names

    assert "myactivity" in prov.finished_activity_names
    assert "myactivity" not in prov.active_activity_names


def test_provenance_json(provenance: Provenance):
    data = json.loads(provenance.as_json())

    activity = data[0]

    assert "python" in activity["system"]
    packages = activity["system"]["python"].get("packages")
    assert isinstance(packages, list)
    assert any(p["name"] == "numpy" for p in packages)
