import io
import unittest
from unittest import mock

import wallet
from wallet import account_type, pending_note


class WalletTest(unittest.TestCase):
    def test_account_types(self):
        self.assertEqual(account_type("0x"), "EOA")
        self.assertEqual(account_type("0xef0100" + "ab" * 20), "EOA, EIP-7702 delegated to 0x" + "ab" * 20)
        self.assertEqual(account_type("0x60806040"), "contract (4 bytes)")

    def test_pending_note(self):
        self.assertEqual(pending_note(5, 5), "no pending txs")
        self.assertEqual(pending_note(5, 7), "2 pending tx(s) stuck")


class ChainsArgTest(unittest.TestCase):
    ADDR = "0x" + "11" * 20

    def run_main(self, chains):
        # Runs main() with --chains and no network; stderr is kept in self.err.
        argv = ["wallet.py", self.ADDR, "--chains", chains]
        self.err = io.StringIO()
        with mock.patch("sys.argv", argv), mock.patch("wallet.check") as check, \
                mock.patch("sys.stdout", new_callable=io.StringIO), \
                mock.patch("sys.stderr", self.err):
            check.return_value = ("Chain", "0.000000 ETH", 0, "no pending txs", "EOA")
            wallet.main()
        return check

    def assert_usage_error(self, chains):
        with self.assertRaises(SystemExit) as cm:
            self.run_main(chains)
        self.assertEqual(cm.exception.code, 2)
        return self.err.getvalue()

    def test_unknown_chain_is_an_error(self):
        err = self.assert_usage_error("ethereum,base")
        self.assertIn("ethereum", err)
        for key in wallet.CHAINS:
            self.assertIn(key, err)

    def test_all_unknown_chains_is_an_error(self):
        self.assert_usage_error("foo,bar")

    def test_empty_chains_is_an_error(self):
        self.assert_usage_error("")

    def test_known_chains_are_checked(self):
        check = self.run_main("eth, base")
        self.assertEqual([c.args[0] for c in check.call_args_list], ["eth", "base"])


if __name__ == "__main__":
    unittest.main()
