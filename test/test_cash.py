import unittest

from finance.cash import *


class TestSuite(unittest.TestCase):
    def setUp(self):
        pass

    def test_get_ss_taxable(self):
        variations = [
            (0, 10000, "mfj", 0),
            (20000, 50000, "mfj", 6850),
            (10000, 30000, "sng", 0),
            (20000, 30000, "sng", 5350),
        ]

        for v in variations:
            self.assertEqual(get_ss_taxable(v[0], v[1], status=v[2]), v[3], msg=v)

    def test_items_total(self):
        data = [
            ("foo", 100, ["foo", "bar"]),
            ("foo", 200, ["foo", "bar"]),
        ]
        self.assertEqual(items_total(data), 300)

    def test_items_total_empty(self):
        data = []
        self.assertEqual(items_total(data), 0)

    def test_items_without_tag(self):
        inp_tag = "fica"
        inp_with = [("roth", 100, ["fed", "sal", inp_tag])]
        inp_wout = [("roth", 100, ["fed", "sal"])]

        self.assertEqual(items_without_tag(inp_with + inp_wout, inp_tag), inp_wout)

    def test_items_with_tag(self):
        inp_tag = "fica"
        inp_with = [("roth", 100, ["fed", "sal", inp_tag])]
        inp_wout = [("roth", 100, ["fed", "sal"])]

        self.assertEqual(items_with_tag(inp_with + inp_wout, inp_tag), inp_with)

    def test_divide(self):
        self.assertEqual(divide(100, 200), 0.5)
        self.assertEqual(divide(100, 0), 0)

    def test_compute_tax(self):
        inp_table = {0: 0.10, 10000: 0.20}
        inp_income = 20000

        exp_bd2 = [10000, 0.2, 2000.0, -1.0]
        exp_bd1 = [10000, 0.1, 1000.0, 0]
        exp_tax = 3000
        exp = (exp_tax, [exp_bd2, exp_bd1])

        self.assertEqual(compute_tax(inp_table, inp_income), exp)
