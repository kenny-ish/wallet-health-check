import unittest

from wallet import account_type, pending_note


class WalletTest(unittest.TestCase):
    def test_account_types(self):
        self.assertEqual(account_type("0x"), "EOA")
        self.assertEqual(account_type("0xef0100" + "ab" * 20), "EOA, EIP-7702 delegated to 0x" + "ab" * 20)
        self.assertEqual(account_type("0x60806040"), "contract (4 bytes)")

    def test_pending_note(self):
        self.assertEqual(pending_note(5, 5), "no pending txs")
        self.assertEqual(pending_note(5, 7), "2 pending tx(s) stuck")


if __name__ == "__main__":
    unittest.main()
