# UnitsDB for Python

The wheel embeds the source-pinned UnitsDB dataset and its producer lookup
tables. `unitsdb.manifest()` exposes the source revision, asset SHA-256 seals,
and collection and lookup inventories.

Use `unitsdb.records(unitsdb.Collection.UNITS)` to enumerate records and
`unitsdb.find(unitsdb.Lookup.UNIT_SYMBOL, "m")` to look up a unit. Records
keep conversion factors and other decimal strings as supplied by the source.
Unknown keys return `None`. Currency alpha codes ignore ASCII case, and
numeric codes use their three-digit strings.
