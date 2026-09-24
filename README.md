# wallet-health-check

One command to see the state of an address on every major EVM chain.

```bash
python wallet.py 0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045
python wallet.py 0x... --chains eth,base,bsc
```

Per chain, in parallel:

- native balance
- **stuck transactions**: `eth_getTransactionCount(addr, "pending")` greater than `"latest"`
  means transactions are waiting in that node's mempool (usually underpriced), which blocks every
  later transaction from the same account
- **account type**: EOA, contract, or an EOA that has **delegated its code via EIP-7702**
  (code `0xef0100 ++ address`). An unexpected delegation is a red flag: the delegate contract can
  act on the account's behalf, and some drainers trick users into signing one

Chains and RPCs are listed in `CHAINS`; add your own. A chain that fails is reported with its
error while the others still show.

## Tests

```bash
python -m unittest -v
```
