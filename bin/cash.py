#!/usr/bin/env python3

import argparse
import sys
import yaml

from os.path import abspath, basename, dirname, join

sys.path.append(dirname(dirname(abspath(__file__))))

from finance.cash import compute_tax
from finance.cash import divide
from finance.cash import fmt_breakdown
from finance.cash import total
from finance.cash import p


def main(argv):
    parser = argparse.ArgumentParser(basename(__file__))

    parser.add_argument("--status", default="mfj", choices=["mfj", "sng", "hoh"])
    parser.add_argument("irs_yaml")
    parser.add_argument("cash_yaml")

    args = parser.parse_args(argv[1:])

    with open(args.irs_yaml) as f:
        db_irs = yaml.load(f.read(), Loader=yaml.SafeLoader)

    with open(args.cash_yaml) as f:
        db_cash = yaml.load(f.read(), Loader=yaml.SafeLoader)

    build_model(db_irs, db_cash, args.status)

    # report_work(db, db_irs, args.status)


def cash_table(entries):
    """
    [[name, amount, [tags...]], ...]
    [
        ['salary', 138690, ['fed', 'fica', 'sal']],
        ['ltcg', 4382, ['cap']]
    ]
    """
    return [[e[0], e[1], e[2:]] for e in entries]


def build_model(db_irs, db_cash, status):
    cash_inc = cash_table(db_cash["income"])
    cash_out_mine = cash_table(db_cash["outflows"]["mine"])
    cash_out_work = cash_table(db_cash["outflows"]["work"])

    irs_med = db_irs["fica"]["medicare"]
    irs_ssa = db_irs["fica"]["oasdi"]
    irs_inc = db_irs["bracket"][status]
    irs_cap = db_irs["cap_gains"][status]

    tot_inc = total(cash_inc, "fed")
    tot_cap = total(cash_inc, "cap")
    tot_fca = total(cash_inc, "fica")

    ded_std = db_irs["standard_deduction"][status]
    ded_inc = total(cash_out_mine, "ded/fed")
    ded_fca = total(cash_out_mine, "ded/fica")

    agi = tot_inc + tot_cap - ded_inc

    tbl_inc = tot_inc - ded_inc - ded_std
    tbl_tot = tbl_inc + tot_cap
    tbl_fca = tot_fca - ded_fca

    tax_inc, tax_inc_brk = compute_tax(irs_inc, tbl_inc)
    tax_cap, tax_cap_brk = compute_tax(irs_cap, tbl_tot)
    tax_ssa, tax_ssa_brk = compute_tax(irs_ssa, tbl_fca)
    tax_med, tax_med_brk = compute_tax(irs_med, tbl_fca)

    tax_fca = tax_ssa + tax_med
    tax_fed = tax_inc + tax_cap

    eff_fed = divide(tax_fed, (tot_inc + tot_cap))

    sal = total(cash_inc, "sal")

    ret_mine = total(cash_out_mine, "ret")
    ret_mine_pct = divide(ret_mine, sal)

    ret_work = total(cash_out_work, "ret")
    ret_work_pct = divide(ret_work, sal)

    ret = ret_mine + ret_work
    ret_pct = divide(ret, sal)

    real_inc = total(cash_inc, "-conv")
    real_out = total(cash_out_mine)
    real_rem = real_inc - real_out - tax_fca - tax_fed

    # -------------------------------------------------------------------------------------------------

    p("  tot_inc", tot_inc)
    p("- ded_inc", -1 * ded_inc)
    p("+ tot_cap", tot_cap)
    p("= agi", agi)
    p("- ded_std", -1 * ded_std)
    p("= tbl_tot", tbl_tot)

    p()
    p("  tax_inc", tax_inc)
    p("+ tax_cap", tax_cap)
    p("= tax_fed", tax_fed)
    p()
    p("eff_fed", eff_fed)

    p()

    p("tax_inc_brk:")
    p(fmt_breakdown(tax_inc_brk))

    p()

    p("tax_cap_brk:")
    p(fmt_breakdown(tax_cap_brk))

    p()

    p("  tot_fca", tot_fca)
    p("- ded_fca", -1 * ded_fca)
    p("= tbl_fca", tbl_fca)

    p()
    p("tax_fca", tax_fca)
    p()

    p("tax_ssa_brk:")
    p(fmt_breakdown(tax_ssa_brk))

    p()

    p("sal", sal)
    p("ret_mine", ret_mine, ret_mine_pct)
    p("ret_mine", ret_work, ret_work_pct)
    p("ret", ret, ret_pct)

    p()

    p("  real_inc", real_inc)
    p("- real_out", real_out * -1)
    p("= real_rem", real_rem)


if __name__ == "__main__":
    main(sys.argv)
