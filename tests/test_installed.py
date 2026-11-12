import hashlib
import importlib.resources
import json
import unittest

import unitsdb


class InstalledDataTests(unittest.TestCase):
    def test_packaged_bytes_match_sealed_manifest(self):
        assets = importlib.resources.files("unitsdb").joinpath("data")
        manifest = json.loads(assets.joinpath("manifest.json").read_text())
        for name in ("unitsdb.json", "lookup-index.json"):
            with self.subTest(asset=name):
                self.assertIn(hashlib.sha256(assets.joinpath(name).read_bytes()).hexdigest(),
                              json.dumps(manifest))
        self.assertEqual(unitsdb.dataset_bytes(), assets.joinpath("unitsdb.json").read_bytes())

    def test_every_lookup_resolves_its_sealed_record(self):
        assets = importlib.resources.files("unitsdb").joinpath("data")
        dataset = json.loads(assets.joinpath("unitsdb.json").read_bytes())
        index = json.loads(assets.joinpath("lookup-index.json").read_bytes())
        for kind, entries in index.items():
            for key, (collection, offset) in entries.items():
                with self.subTest(kind=kind, key=key):
                    self.assertEqual(unitsdb.find(kind, key), dataset[collection][offset])
        for collection in unitsdb.Collection:
            self.assertEqual(unitsdb.records(collection), dataset[collection.value])

    def test_final_unitsdb_data_revision(self):
        self.assertEqual(unitsdb.manifest()["producer"]["commit"], "2f27dbd6a664fde498455159cccbf2fb2e78f154")
        self.assertEqual(unitsdb.provenance()["data"]["commit"], "b210137fd87c493ad437468c925c98ec921a4468")
        # UnitsDB b210137 defines the US hundredweight as hecto-pound.
        cwt = unitsdb.find("unit_id", "NISTu230")
        self.assertEqual(cwt["root_units"], [{
            "power": 1, "unit_reference": {"id": "NISTu201"}, "prefix_reference": {"id": "NISTp10_2"},
        }])

    def test_lookup_case_unknown_and_invalid_kinds(self):
        self.assertEqual(unitsdb.find("currency_code", "usd"),
                         unitsdb.find("currency_code", "USD"))
        self.assertIsNone(unitsdb.find("unit_symbol", "not-a-unit-827364"))
        with self.assertRaises(ValueError):
            unitsdb.find("not-a-kind", "m")
        with self.assertRaises(ValueError):
            unitsdb.records("not-a-collection")

    def test_returned_records_are_detached(self):
        original = unitsdb.find("unit_symbol", "m")
        self.assertIsNotNone(original)
        changed = unitsdb.find("unit_symbol", "m")
        changed["caller_mutation"] = True
        self.assertEqual(unitsdb.find("unit_symbol", "m"), original)
        records = unitsdb.records("units")
        records.clear()
        self.assertTrue(unitsdb.records("units"))
