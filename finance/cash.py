import sys


def compute_tax(tax_table, balance):
    """
    To compute taxes we start with the highest brackets, apply the taxes, remove that amount,
    and then move to the smaller bracket.
    """

    tax_total = 0
    last_bottom = None
    breakdown = []

    for bottom in sorted(tax_table, reverse=True):
        if balance > bottom:
            taxable = balance - bottom
            balance = balance - taxable
            tax_rate = tax_table[bottom]
            tax_amount = taxable * tax_rate
            tax_total = tax_total + tax_amount

            if last_bottom:
                head_room = last_bottom - bottom - taxable
            else:
                head_room = -1.0

            breakdown.append(
                [
                    taxable,
                    tax_rate,
                    tax_amount,
                    head_room,
                ]
            )

        last_bottom = bottom

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
    if status == "mfj":
        tier_1, tier_2 = 32000, 44000
    else:
        tier_1, tier_2 = 25000, 34000

    ss_taxable = 0

    prov_income = income + (ss_income / 2)

    if prov_income > tier_1:
        ss_taxable = ss_taxable + min(prov_income - tier_1, (tier_2 - tier_1)) * 0.50

    if prov_income > tier_2:
        ss_taxable = ss_taxable + (prov_income - tier_2) * 0.85

    return min(ss_taxable, ss_income * 0.85)


def items_total(data):
    return sum(i[1] for i in data)


def total(data, tag=None):
    if tag:
        if tag.startswith("-"):
            data = [i for i in data if tag[1:] not in i[2]]
        else:
            data = [i for i in data if tag in i[2]]

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
