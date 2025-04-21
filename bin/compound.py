#!/usr/bin/env python3

import argparse
import sys

from os.path import basename


def main(argv):
    parser = argparse.ArgumentParser(basename(__file__))

    parser.add_argument("--years", type=int, default=1)
    parser.add_argument("--rate", type=float, default=0.05)
    parser.add_argument("--add", type=int, default=0)
    parser.add_argument("balance", type=int)

    args = parser.parse_args(argv[1:])

    balance = args.balance

    for year in range(1, args.years + 1):
        balance = balance * (1 + args.rate)

        print(year, round(balance), round(balance * 0.04))

        balance = balance + args.add


if __name__ == "__main__":
    main(sys.argv)
