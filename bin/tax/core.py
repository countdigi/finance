import unittest


def compute_tax(tax_table, balance):
    """
    To compute taxes we start with the highest brackets, apply the taxes, remove that amount, and then move to the smaller bracket.
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
                    int(amount_taxable_at_bracket),
                    bracket_tax_rate,
                    int(bracket_tax_amount),
                    int(head_room),
                ]
            )

        last_bracket_bottom = bracket_bottom

    return tax_total, breakdown


# ----------------------------------------------------------------------------------------------------
# Test suite
# ----------------------------------------------------------------------------------------------------


class Test(unittest.TestCase):
    def setUp(self):
        pass

    def test_compute_tax(self):
        in_tax_table = {0: 0.10, 20000: 0.20}
        in_balance = 30000

        expected = [[10000, 0.2, 2000, -1], [20000, 0.1, 2000, 0]]

        self.assertEqual(compute_tax(in_tax_table, in_balance), expected)


if __name__ == "__main__":
    unittest.main()
