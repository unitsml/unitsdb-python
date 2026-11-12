"""Look up records in the bundled UnitsDB projection."""

from copy import deepcopy
from enum import Enum
from functools import lru_cache
from importlib.resources import files
import json


class Collection(str, Enum):
    UNITS = "units"
    PREFIXES = "prefixes"
    DIMENSIONS = "dimensions"
    QUANTITIES = "quantities"
    CURRENCIES = "currencies"
    SCALES = "scales"


class Lookup(str, Enum):
    UNIT_SYMBOL = "unit_symbol"
    UNIT_ID = "unit_id"
    UNIT_URI = "unit_uri"
    PREFIX_SYMBOL = "prefix_symbol"
    PREFIX_ID = "prefix_id"
    DIMENSION_ID = "dimension_id"
    QUANTITY_ID = "quantity_id"
    CURRENCY_CODE = "currency_code"
    CURRENCY_NUMERIC = "currency_numeric"
    SCALE_ID = "scale_id"
    RECORD_ID = "record_id"


def _asset(name):
    return files(__package__).joinpath("data", name).read_bytes()


@lru_cache(maxsize=2)
def _json(name):
    return json.loads(_asset(name))


def dataset_bytes():
    """Return the exact producer dataset bytes."""
    return _asset("unitsdb.json")


def manifest():
    """Return the asset provenance, hashes, and inventory."""
    return json.loads(_asset("manifest.json"))


def records(collection):
    """Return the records of a register collection in producer order."""
    return deepcopy(_json("unitsdb.json")[Collection(collection).value])


def find(kind, key):
    """Find an exact key, returning None for an unknown record."""
    kind = Lookup(kind)
    if kind is Lookup.CURRENCY_CODE and key.isascii():
        key = key.upper()
    location = _json("lookup-index.json")[kind.value].get(key)
    if location is None:
        return None
    table, offset = location
    return deepcopy(_json("unitsdb.json")[table][offset])


def provenance():
    """Return source release and generation metadata."""
    return deepcopy(_json("unitsdb.json")["provenance"])
