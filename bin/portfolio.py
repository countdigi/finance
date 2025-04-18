#!/usr/bin/env python3

import argparse
import sys

from os.path import abspath, basename, dirname

sys.path.append(dirname(dirname(abspath(__file__))))


from finance import portfolio


def fmt_pct(pct, fractional=None):
    if fractional:
        return f"{round(pct * 100, 1):>4}"
    else:
        return f"{round(pct * 100):>2}"


def fmt_amt(amt, fractional=None):
    if fractional:
        return f"{amt:>6.1f}"
    else:
        return f"{round(amt):>4}"


def main(argv):
    parser = argparse.ArgumentParser(basename(__file__))

    parser.add_argument(
        "--fractional",
        "-f",
        action="store_true",
        help="display fractional allocation percentages",
    )
    parser.add_argument("portfolio_txt")

    args = parser.parse_args(argv)

    col_spec = []

    amt_spec = ["eqt", "fix"]

    with open(args.portfolio_txt) as f:
        cols = f.readline().rstrip("\n").split()

        for col in cols[1:]:
            col_spec.append(col.split("/"))

        for line in f:
            entries = []

            cols = line.rstrip("\n").split()

            entry_date = cols[0]

            for col_idx, col in enumerate(cols[1:]):
                for amt_idx, amt in enumerate(col.split(",")):
                    entries.append(
                        portfolio.Entry(
                            date=entry_date,
                            name=col_spec[col_idx][0],
                            taxclass=col_spec[col_idx][1],
                            asset=amt_spec[amt_idx],
                            amount=float(amt),
                        )
                    )

            asset_total = portfolio.total_by(entries, "asset")
            asset_alloc = portfolio.get_alloc(asset_total)
            asset = {k: (asset_total[k], asset_alloc[k]) for k in asset_total}

            taxclass_total = portfolio.total_by(entries, "taxclass")
            taxclass_alloc = portfolio.get_alloc(taxclass_total)
            taxclass = {
                k: (taxclass_total[k], taxclass_alloc[k]) for k in taxclass_total
            }

            print(
                "".join(
                    [
                        str(entry_date),
                        " | ",
                        str(fmt_amt(sum(asset_total.values()), args.fractional)),
                        " | ",
                        "/".join(asset),
                        " ",
                        ",".join(
                            fmt_amt(v[0], args.fractional) for v in asset.values()
                        ),
                        " ",
                        "(",
                        "/".join(
                            fmt_pct(v[1], args.fractional) for v in asset.values()
                        ),
                        ")",
                        " | ",
                        "/".join(taxclass),
                        " ",
                        ",".join(
                            fmt_amt(v[0], args.fractional) for v in taxclass.values()
                        ),
                        " ",
                        "(",
                        "/".join(
                            fmt_pct(v[1], args.fractional) for v in taxclass.values()
                        ),
                        ")",
                    ]
                )
            )


if __name__ == "__main__":
    main(sys.argv[1:])
