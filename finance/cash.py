import unittest


def compute_tax(tax_table, balance):
    """
    To compute taxes we start with the highest brackets, apply the taxes, remove that amount,
    and then move to the smaller bracket.
    """

    tax_total = 0
    last_bracket_bottom = None
    breakdown = []

    for bracket_bottom in sorted(tax_table, reverse=True):
        if balance > bracket_bottom:
            amount_taxable_at_bracket = balance - bracket_bottom
            balance = balance - amount_taxable_at_bracket
            bracket_tax_rate = tax_table[bracket_bottom]
            bracket_tax_amount = amount_taxable_at_bracket * bracket_tax_rate
            tax_total = tax_total + bracket_tax_amount

            if last_bracket_bottom:
                head_room = (
                    last_bracket_bottom - bracket_bottom - amount_taxable_at_bracket
                )
            else:
                head_room = -1.0

            breakdown.append(
                [
                    amount_taxable_at_bracket,
                    bracket_tax_rate,
                    bracket_tax_amount,
                    head_room,
                ]
            )

        last_bracket_bottom = bracket_bottom

    return tax_total, breakdown


def divide(divisor, dividend):
    return divisor / dividend if dividend != 0 else 0


def fmt_breakdown(breakdown, offset=21):
    """
     Return formatted breakdown. E.g.:
       tax (amount_taxed @ rate) [remaining_in_bracket]
    430.10 (     1955.00 @ 0.22) [99345.00]
    """

    return "\n".join(
        " " * offset
        + f"{item[2]:>9.2f} ({item[0]:-9.2f} @ {item[1]:0.4f}) [{item[3]:-9.2f} space-left]"
        for item in breakdown
    )


def get_ss_taxable(income, ss_income, status="mfj"):
    if status not in ["sng", "mfj", "hoh"]:
        sys.exit(1)

    if status == "sng" or status == "hoh":
        tier_1, tier_2 = 25000, 34000
    if status == "mfj":
        tier_1, tier_2 = 32000, 44000

    ss_taxable = 0

    prov_income = income + (ss_income / 2)

    if prov_income > tier_1:
        ss_taxable = ss_taxable + min(prov_income - tier_1, (tier_2 - tier_1)) * 0.50

    if prov_income > tier_2:
        ss_taxable = ss_taxable + (prov_income - tier_2) * 0.85

    return min(ss_taxable, ss_income * 0.85)


def items_total(data):
    return sum(i[1] for i in data)


def items_with_tag(data, tag):
    """
    Return items which have <tag>.
    """
    return [i for i in data if tag in i[2]]


def items_without_tag(data, tag):
    """
    Return items with <tag>.
    """
    return [i for i in data if tag not in i[2]]


def p(*args, test=False):
    str = ""

    if len(args) == 1:
        str = "{:<18}".format(*args)

    elif len(args) == 2:
        str = "{:<18}: {:>10.3f}".format(*args)

    elif len(args) == 3:
        str = "{:<18}: {:>10.3f} ({:>.3f})".format(*args)

    if test:
        return str
    else:
        print(str)


if __name__ == "__main__":
    unittest.main()
