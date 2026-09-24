# wallet-health-check

Checks one address on Ethereum, Base, Arbitrum, OP Mainnet, BNB Chain and Polygon at the same time.

```bash
python wallet.py 0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045
python wallet.py 0x... --chains eth,base,bsc
```

For each chain it shows

- the native balance,
- stuck transactions. If `eth_getTransactionCount(addr, "pending")` is higher than for `"latest"`,
  transactions are waiting in that node's mempool, usually because they're underpriced, and they
  block every later transaction from the account.
- the account type: EOA, contract, or an EOA that delegated its code with EIP-7702 (code
  `0xef0100 ++ address`). An unexpected delegation is a warning sign, because the delegate contract
  can act for the account, and some drainers trick people into signing one.

Chains and RPCs are listed in `CHAINS`. If one chain fails, its error is shown and the rest still
print.

## Tests

```bash
python -m unittest -v
```
