#!/usr/bin/env python3

import argparse
import datetime
import json
import sys
import yaml

from os.path import abspath, basename, dirname, join

from tax.core import compute_tax


def main(argv):
    basedir = dirname(abspath(__file__))

    parser = argparse.ArgumentParser(basename(__file__))

    parser.add_argument("--inc-w2", help="w2 income", default="0")
    parser.add_argument("--inc-lt", default="0", help="long-term capital gains")
    parser.add_argument(
        "--inc-un", default="0", help="short-term gains, rental income, etc"
    )
    parser.add_argument(
        "--ret-fed", default="0", help="fed tax deductible retirement contributions"
    )
    parser.add_argument(
        "--ret-fica", default="0", help="fica deductible retirement contributions (hsa)"
    )
    parser.add_argument(
        "--ret-tax",
        default="0",
        help="taxable retirement contributions (roth, brokerage)",
    )
    parser.add_argument("--ded-fed", default="0", help="federal deductions")
    parser.add_argument(
        "--ded-fica", default="0", help="fica deductions (health insurance premiums)"
    )
    parser.add_argument(
        "--separator", default=",", help="separator for option multiple inputs"
    )
    parser.add_argument("--status", default="mfj", choices=["mfj", "sng", "hoh"])
    parser.add_argument("--age", default=18)
    parser.add_argument("--age-spouse", default=18)
    parser.add_argument("irs_yaml", nargs="?", default="irs/2024.yaml")

    args = parser.parse_args(argv[1:])


    status = args.status

    inc_w2 = sum(int(x) for x in args.inc_w2.split(args.separator))
    inc_lt = sum(int(x) for x in args.inc_lt.split(args.separator))
    inc_un = sum(int(x) for x in args.inc_un.split(args.separator))

    inc = inc_w2 + inc_lt + inc_un

    with open(args.irs_yaml) as f:
        db = yaml.load(f.read(), Loader=yaml.SafeLoader)

    std = db["status"][status]["std_ded"]
    tt_or = db["status"][status]["tax"]
    tt_lt = db["status"][status]["cap_gains"]
    tt_niit = db["status"][status]["niit"]

    print("irs_yaml: ", args.irs_yaml, file=sys.stderr)
    print("status:   ", status, file=sys.stderr)
    print("std_ded:  ", std, file=sys.stderr)
    print("inc_w2:   ", inc_w2, file=sys.stderr)
    print("inc_un:   ", inc_un, file=sys.stderr)
    print("inc_lt:   ", inc_lt, file=sys.stderr)
    print(file=sys.stderr)

    tax_ss, tax_ss_tab = compute_tax(db["fica"]["oasdi"], inc_w2)
    tax_med, tax_med_tab = compute_tax(db["fica"]["medicare"], inc_w2)

    tax_or, tax_or_tab = compute_tax(tt_or, inc_w2 + inc_un - std)

    tax_lt, tax_lt_tab = compute_tax(tt_lt, inc - std)
    tax_lt = (
        tax_lt - compute_tax(tt_lt, inc - std - inc_lt)[0]
    )  # remove non long-term taxes to get cap_gains "on-the-top"

    tax_niit, tax_niit_tab = compute_tax(tt_niit, inc)
    tax_niit = min(
        tax_niit, (inc_lt + inc_un) * 0.038
    )  # make sure only lt and unearned income is used for niit

    tax = tax_or + tax_lt + tax_niit

    print(f"income: {int(inc):>6d} / tax: {int(tax):>6d} / tax-eff: {tax / inc:>6.2%}")


if __name__ == "__main__":
    main(sys.argv)

# {
#   "fica": {
#     "oasdi": {
#       "0": 0.062,
#       "168600": 0
#     },
#     "medicare": {
#       "0": 0.0145
#     }
#   },
#   "status": {
#     "mfj": {
#       "std_ded": 29200,
#       "std_ded_65_or_blind": 1550,
#       "tax": {
#         "0": 0.1,
#         "23200": 0.12,
#         "94300": 0.22,
#         "201050": 0.24,
#         "383900": 0.32,
#         "487450": 0.35,
#         "731200": 0.37
#       },
#       "cap_gains": {
#         "0": 0,
#         "94050": 0.15,
#         "583750": 0.2
#       },
#       "niit": 250000,
#       "ira": {
#         "roth_phaseout": {
#           "start": 230000,
#           "max": 240000
#         },
#         "trad_phaseout": {
#           "covered": {
#             "start": 123000,
#             "max": 143000
#           },
#           "not_covered": {
#             "start": 230000,
#             "max": 240000
#           }
#         }
#       },
#       "savers_credit": {
#         "76500": 0.1,
#         "50000": 0.2,
#         "46000": 0.5
#       }
#     },
#     "sng": {
#       "std_ded": 14600,
#       "std_ded_65_or_blind": 1950,
#       "tax": {
#         "0": 0.1,
#         "11600": 0.12,
#         "47150": 0.22,
#         "100525": 0.24,
#         "191950": 0.32,
#         "243725": 0.35,
#         "609350": 0.37
#       },
#       "cap_gains": {
#         "0": 0,
#         "47025": 0.15,
#         "518900": 0.2
#       },
#       "niit": 200000,
#       "ira": {
#         "roth_phaseout": {
#           "start": 146000,
#           "max": 161000
#         },
#         "trad_phaseout": {
#           "covered": {
#             "start": 77000,
#             "max": 87000
#           }
#         }
#       },
#       "savers_credit": {
#         "38250": 0.1,
#         "25000": 0.2,
#         "23000": 0.5
#       }
#     },
#     "hoh": {
#       "std_ded": 21900,
#       "std_ded_65_or_blind": 1550,
#       "tax": {
#         "0": 0.1,
#         "16550": 0.12,
#         "63100": 0.22,
#         "100500": 0.24,
#         "191950": 0.32,
#         "243700": 0.35,
#         "609350": 0.37
#       },
#       "cap_gains": {
#         "0": 0,
#         "63000": 0.15,
#         "551350": 0.2
#       },
#       "niit": 200000,
#       "ira": {
#         "roth_phaseout": {
#           "start": 146000,
#           "max": 161000
#         },
#         "trad_phaseout": {
#           "covered": {
#             "start": 77000,
#             "max": 87000
#           }
#         }
#       },
#       "savers_credit": {
#         "57375": 0.1,
#         "37500": 0.2,
#         "34500": 0.5
#       }
#     }
#   },
#   "retirement": {
#     "415c": {
#       "limit": 69000
#     },
#     "403b": {
#       "regular": 23000,
#       "catchup": 7500
#     },
#     "457b": {
#       "regular": 23000,
#       "catchup": 7500
#     },
#     "ira": {
#       "regular": 7000,
#       "catchup": 1000
#     },
#     "hsa": {
#       "fam": {
#         "limit": 8300,
#         "catchup": 1000,
#         "min-ded": 3200,
#         "oop": 16100
#       },
#       "sng": {
#         "limit": 4150,
#         "catchup": 1000,
#         "min-ded": 1600,
#         "oop": 8050
#       }
#     }
#   },
#   "gift_exclusion": 18000,
#   "medicare": {
#     "part_b": 174.7
#   }
# }
