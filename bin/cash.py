#!/usr/bin/env python3

import argparse
import datetime
import sys
import yaml

from os.path import abspath, basename, dirname, join

sys.path.append(dirname(dirname(abspath(__file__))))

from finance.cash import compute_tax
from finance.cash import divide
from finance.cash import fmt_breakdown
from finance.cash import items_total, items_with_tag, items_without_tag, total
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

    p("tax_inc breakdown")
    p(fmt_breakdown(tax_inc_brk))

    p()

    p("tax_cap breakdown")
    p(fmt_breakdown(tax_cap_brk))


def report_work(db, db_irs, status):
    income, out_mine, out_work = [], [], []

    if "income" in db:
        income = [[f[0], int(f[1]), [*f[2:]]] for f in db["income"]]

    if "outflows" in db and "mine" in db["outflows"]:
        out_mine = [[f[0], int(f[1]), [*f[2:]]] for f in db["outflows"]["mine"]]

    if "outflows" in db and "work" in db["outflows"]:
        out_work = [[f[0], int(f[1]), [*f[2:]]] for f in db["outflows"]["work"]]

    irs_med = db_irs["fica"]["medicare"]
    irs_ss = db_irs["fica"]["oasdi"]
    std_ded = db_irs["standard_deduction"][status]
    irs_fed = db_irs["bracket"][status]

    fed_inc = items_total(items_with_tag(income, "fed"))
    fica_inc = items_total(items_with_tag(income, "fica"))

    conversions = items_total(items_with_tag(income, "conv"))
    interest = items_total(items_with_tag(income, "interest"))

    fed_ded = items_total(items_with_tag(out_mine, "ded/fed"))
    fica_ded = items_total(items_with_tag(out_mine, "ded/fica"))

    agi = fed_inc - fed_ded
    fed_taxable = agi - std_ded
    fica_taxable = fica_inc - fica_ded

    fed_tax, fed_tax_breakdown = compute_tax(irs_fed, fed_taxable)
    tax_ss, tax_ss_breakdown = compute_tax(irs_ss, fica_taxable)
    tax_med, tax_med_breakdown = compute_tax(irs_med, fica_taxable)
    tax_fica = tax_ss + tax_med

    fed_tax_eff = divide(fed_tax, fed_inc)

    tax_ss_eff = divide(tax_ss, fica_inc)

    ret_me = items_total(items_with_tag(out_mine, "ret"))
    ret_work = items_total(items_with_tag(out_work, "ret"))
    ret = ret_me + ret_work

    salary = items_total(items_with_tag(income, "sal"))
    ret_pct = divide(ret, salary)

    ret_pct_me = divide(ret_me, salary)
    ret_pct_work = divide(ret_work, salary)

    real_inc = items_total(items_without_tag(income, "conv"))
    real_out = items_total(out_mine)
    real_tax = fed_tax + tax_ss + tax_med
    real_left = real_inc - real_out - real_tax

    # -----------------------------------------------------------------
    # Report
    # -----------------------------------------------------------------

    p("  fed_inc", fed_inc)
    p("- fed_ded", -1 * fed_ded)
    p("= agi", agi)
    p("- std_ded", -1 * std_ded)
    p("= fed_taxable", fed_taxable)
    p()
    p("fed_tax_breakdown")
    p(fmt_breakdown(fed_tax_breakdown))

    p("fed_tax", fed_tax)
    p("fed_tax_eff", fed_tax_eff)
    p()
    p("  fica_inc", fica_inc)
    p("- fica_ded", -1 * fica_ded)
    p("= fica_taxable", fica_taxable)
    p()
    p("tax_ss_breakdown")
    p(fmt_breakdown(tax_ss_breakdown))
    p("  tax_ss", tax_ss)
    p("+ tax_med", tax_med)
    p("= tax_fica", tax_fica)
    p()
    p("  real_inc", real_inc)
    p("- real_out", real_out * -1)
    p("- real_tax", real_tax * -1)
    p("= real_year", real_left)
    p("= real_month", real_left / 12)
    p()
    p("ret_me", ret_me, ret_pct_me)
    p("ret_work", ret_work, ret_pct_work)
    p("ret", ret, ret_pct)
    p()

    if "income" in db:
        p("income:")
        for x in db["income"]:
            print("  {:<18} {:>9.2f} {}".format(x[0], x[1], x[2:]))

        p()

    if "outflows" in db:
        for k in ["mine", "work"]:
            if k in db["outflows"]:
                print("out/" + k + ":")
                for x in db["outflows"][k]:
                    print("  {:<18} {:>9.2f} {}".format(x[0], x[1], x[2:]))


if __name__ == "__main__":
    main(sys.argv)
