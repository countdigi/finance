#!/usr/bin/env python3

"""
Parses a portfolio data file, calculates asset and tax class allocations,
and prints a formatted summary for each entry date.
"""

import argparse
import sys

from os.path import abspath, basename, dirname

from typing import TextIO, Tuple, List

sys.path.append(dirname(dirname(abspath(__file__))))


from finance import portfolio


def fmt_pct(pct: float, fractional: bool = False) -> str:
    """Formats a percentage value"""

    if fractional:
        return f"{round(pct * 100, 1):>4}"
    else:
        return f"{round(pct * 100):>2}"


def fmt_amt(amt: float, fractional: bool = False) -> str:
    """Formats an amount value"""

    if fractional:
        return f"{amt:>6.1f}"
    else:
        return f"{round(amt):>4}"


def get_col_spec(header_line: str) -> list[Tuple[str, str]]:
    """Parses the header line to get column specifications."""

    cols = header_line.rstrip("\n").split()

    col_spec = [tuple(col.split("/")) for col in cols[1:]]

    for idx, spec in enumerate(col_spec, start=2):
        if len(spec) != 2:
            sys_exit(
                f"Invalid header format. Each column spec after date must be 'name/taxclass' at column: {idx}"
            )

    return col_spec  # type: ignore


def process_portfolio_file(f: TextIO, fractional: bool = False):
    col_spec = get_col_spec(f.readline())

    amt_spec = ["eqt", "fix"]

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
        taxclass = {k: (taxclass_total[k], taxclass_alloc[k]) for k in taxclass_total}

        print(
            "".join(
                [
                    str(entry_date),
                    " | ",
                    str(fmt_amt(sum(asset_total.values()), fractional)),
                    " | ",
                    "/".join(asset),
                    " ",
                    ",".join(fmt_amt(v[0], fractional) for v in asset.values()),
                    " ",
                    "(",
                    "/".join(fmt_pct(v[1], fractional) for v in asset.values()),
                    ")",
                    " | ",
                    "/".join(taxclass),
                    " ",
                    ",".join(fmt_amt(v[0], fractional) for v in taxclass.values()),
                    " ",
                    "(",
                    "/".join(fmt_pct(v[1], fractional) for v in taxclass.values()),
                    ")",
                ]
            )
        )


def sys_exit(msg: str):
    print(msg, file=sys.stderr)
    sys.exit(1)


def main(argv):
    parser = argparse.ArgumentParser(basename(__file__))

    parser.add_argument(
        "--fractional",
        "-f",
        action="store_true",
        help="Display fractional allocation percentages and amounts.",
    )
    parser.add_argument("portfolio_txt", help="Path to the portfolio data file.")

    args = parser.parse_args(argv)

    try:
        with open(args.portfolio_txt, "r") as f:
            process_portfolio_file(f, args.fractional)

    except FileNotFoundError:
        sys_exit(f"Error: File not found '{args.portfolio_txt}'")

    except IOError as e:
        sys_exit(f"Error opening or reading file '{args.portfolio_txt}': {e}")

    except Exception as e:
        sys_exit(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    main(sys.argv[1:])
