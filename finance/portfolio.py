from collections import namedtuple


Entry = namedtuple("Entry", ["date", "name", "taxclass", "asset", "amount"])


def total_by(entries, field) -> dict:
    """
    Accepts a list of entries and entry field name and builds a dictionary
    of field name keys each with a value totaling the amount for that key. E.g.:
    {
      "eqt": 800,
      "bnd": 200,
    }
    """

    db = {}

    for entry in entries:
        k = getattr(entry, field)
        db[k] = db.setdefault(k, 0) + entry.amount

    return db


def get_alloc(db) -> dict:
    """
    Accepts a list of entries and entry field name and builds a dictionary
    of field name keys each with the ratio of allocation. E.g.:
    {
      "eqt": 0.8,
      "bnd": 0.2,
    }
    """

    total = sum(v for v in db.values())

    return {k: v / total for k, v in db.items()}
