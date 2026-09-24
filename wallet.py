"""Multi-chain health check for an EVM address."""
import argparse
import json
import urllib.request
from concurrent.futures import ThreadPoolExecutor

CHAINS = {
    "eth": ("Ethereum", "https://ethereum-rpc.publicnode.com", "ETH"),
    "base": ("Base", "https://mainnet.base.org", "ETH"),
    "arb": ("Arbitrum One", "https://arb1.arbitrum.io/rpc", "ETH"),
    "op": ("OP Mainnet", "https://mainnet.optimism.io", "ETH"),
    "bsc": ("BNB Chain", "https://bsc-dataseed.bnbchain.org", "BNB"),
    "polygon": ("Polygon", "https://polygon-bor-rpc.publicnode.com", "POL"),
}


def rpc(url, method, params):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json", "User-Agent": "wallet-health-check"})
    with urllib.request.urlopen(req, timeout=20) as r:
        resp = json.load(r)
    if "error" in resp:
        raise RuntimeError(resp["error"].get("message"))
    return resp["result"]


def account_type(code_hex):
    code = (code_hex or "0x")[2:].lower()
    if not code:
        return "EOA"
    if code.startswith("ef0100") and len(code) == 46:
        return f"EOA, EIP-7702 delegated to 0x{code[6:]}"
    return f"contract ({len(code) // 2} bytes)"


def pending_note(latest, pending):
    gap = pending - latest
    return f"{gap} pending tx(s) stuck" if gap > 0 else "no pending txs"


def check(key, address):
    name, url, symbol = CHAINS[key]
    bal = int(rpc(url, "eth_getBalance", [address, "latest"]), 16)
    latest = int(rpc(url, "eth_getTransactionCount", [address, "latest"]), 16)
    pending = int(rpc(url, "eth_getTransactionCount", [address, "pending"]), 16)
    code = rpc(url, "eth_getCode", [address, "latest"])
    return name, f"{bal / 1e18:,.6f} {symbol}", latest, pending_note(latest, pending), account_type(code)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("address")
    ap.add_argument("--chains", default=",".join(CHAINS))
    a = ap.parse_args()
    keys = [k.strip() for k in a.chains.split(",") if k.strip() in CHAINS]

    with ThreadPoolExecutor(max_workers=len(keys)) as pool:
        futures = {k: pool.submit(check, k, a.address) for k in keys}
    print(f"{'chain':<14}{'balance':>24}{'nonce':>8}  {'mempool':<22}account")
    warnings = []
    for k in keys:
        try:
            name, bal, nonce, note, kind = futures[k].result()
        except Exception as e:
            print(f"{CHAINS[k][0]:<14}  error: {str(e)[:70]}")
            continue
        print(f"{name:<14}{bal:>24}{nonce:>8}  {note:<22}{kind}")
        if "stuck" in note:
            warnings.append(f"{name}: {note}; speed up or replace the lowest pending nonce")
        if "7702" in kind:
            warnings.append(f"{name}: account code is delegated; make sure you authorized {kind.split()[-1]}")
    for w in warnings:
        print("WARNING:", w)


if __name__ == "__main__":
    main()
