#!/usr/bin/env python3

import argparse
import os
import sys


def main(argv):
    parser = argparse.ArgumentParser(os.path.basename(__file__), add_help=True)

    parser.add_argument("--withdraw", default="0", help="amount to withdraw")
    parser.add_argument("balances", help="comma-separated list of balances")
    parser.add_argument("ratios", help="comma-separated list of desired ratios")

    if len(sys.argv) > 1:
        args = parser.parse_args(argv)
    else:
        parser.print_help()
        sys.exit(1)

    balances = [float(x) for x in args.balances.split(",")]
    ratios = [float(x) / 100 for x in args.ratios.split(",")]

    if len(balances) != len(ratios):
        print(
            f"number of amounts ({len(balances)}) and ratios ({len(ratios)}) must match",
            file=sys.stderr,
        )
        sys.exit(1)

    if sum(ratios) != 1:
        print(f"sum(ratios): {sum(ratios)} != 1", file=sys.stderr)
        sys.exit(1)

    withdraw = float(args.withdraw)

    total = sum(balances)

    print(f"cur:")

    for bal in balances:
        rat = bal / total
        print("  ", f"{rat:>5.1%} | {bal:>9.1f}")

    print(f"           {total:9.1f}")

    print()

    print(f"adj:")

    for bal, rat in zip(balances, ratios):
        delta_base = (total * (rat)) - bal
        delta_with = withdraw * rat
        delta = delta_base - delta_with

        new_bal = bal + delta

        print(
            "  ",
            f"{rat:>5.1%} | {new_bal:>9.1f} ({delta_base:>+6.1f} - {delta_with:>6.1f} = {delta:>+6.1f})",
        )

    print(f"           {total - withdraw:>9.1f}")


if __name__ == "__main__":
    main(sys.argv[1:])
