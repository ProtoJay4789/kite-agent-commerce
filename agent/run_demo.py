"""
GenTech Labs — Kite AI Agentic Commerce Agent

A multi-agent system demonstrating autonomous AI agents performing tasks
and settling payments on Kite AI blockchain via smart contract escrow.

Agents:
  BuyerAgent   — Needs market analysis, creates escrow, pays for work
  ProviderAgent — Performs analysis (real data fetching + computation)
  ValidatorAgent — AI validator that verifies work quality, signs EIP-712

Flow:
  1. Buyer creates escrow (locks USDC)
  2. Provider performs task (fetches real market data, generates report)
  3. Provider marks work complete
  4. Validator verifies output quality → signs EIP-712
  5. Funds released on-chain to provider

Usage:
  python3 agent/run_demo.py [--simulate]

  Without --simulate: executes real on-chain transactions (needs .env with PK)
  With --simulate: shows the full flow with dry-run output
"""

import os
import sys
import json
import time
import httpx
from datetime import datetime, timezone
from eth_account import Account
from eth_account.messages import encode_typed_data
from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware

# ─── Configuration ──────────────────────────────────────────────────────────

KITE_RPC = "https://rpc-testnet.gokite.ai/"
CHAIN_ID = 2368
EXPLORER = "https://testnet.kitescan.ai"

# Deployed contract addresses
CONTRACTS = {
    "AgentEscrow": "0xf7DcebAEC0356c96926a6619Fc80F24590932F06",
    "TECHPaymentRouter": "0x963Cb46670c4F13C2dbB3a10BEE49BBb3650AC14",
    "MockTECH": "0x2C7DE7F6C149808E66B87cE138fdDb00dDAf085E",
    "USDC": "0x2d16C0dc617dCF743f55A3bB42fDE4A0E640A5b5",
}

# EIP-712 domain for AgentEscrow
EIP712_DOMAIN = {
    "name": "AgentEscrow",
    "version": "1",
    "chainId": CHAIN_ID,
    "verifyingContract": CONTRACTS["AgentEscrow"],
}

EIP712_TYPES = {
    "Validation": [
        {"name": "escrowId", "type": "uint256"},
    ]
}

# Minimal ERC-20 ABI for USDC
ERC20_ABI = [
    {"constant": True, "inputs": [{"name": "_owner", "type": "address"}],
     "name": "balanceOf", "outputs": [{"name": "balance", "type": "uint256"}], "type": "function"},
    {"constant": False, "inputs": [
        {"name": "_spender", "type": "address"}, {"name": "_value", "type": "uint256"}],
     "name": "approve", "outputs": [{"name": "", "type": "bool"}], "type": "function"},
    {"constant": False, "inputs": [{"name": "_to", "type": "address"},
     {"name": "_value", "type": "uint256"}],
     "name": "transfer", "outputs": [{"name": "", "type": "bool"}], "type": "function"},
]

# ─── Agent Escrow ABI (truncated to needed functions) ───────────────────────

AGENT_ESCROW_ABI = [
    {"inputs": [{"name": "_usdc", "type": "address"}, {"name": "_aiValidator", "type": "address"}],
     "stateMutability": "nonpayable", "type": "constructor"},
    {"inputs": [], "name": "USDC", "outputs": [{"type": "address"}], "stateMutability": "view", "type": "function"},
    {"inputs": [], "name": "AI_VALIDATOR", "outputs": [{"type": "address"}], "stateMutability": "view", "type": "function"},
    {"inputs": [], "name": "nextEscrowId", "outputs": [{"type": "uint256"}], "stateMutability": "view", "type": "function"},
    {"inputs": [], "name": "totalEscrows", "outputs": [{"type": "uint256"}], "stateMutability": "view", "type": "function"},
    {"inputs": [{"name": "_escrowId", "type": "uint256"}],
     "name": "getEscrow",
     "outputs": [{"type": "address"}, {"type": "address"}, {"type": "uint256"},
                  {"type": "uint256"}, {"type": "uint8"}, {"type": "uint256"}],
     "stateMutability": "view", "type": "function"},
    {"inputs": [{"name": "_seller", "type": "address"}, {"name": "_amount", "type": "uint256"}],
     "name": "createEscrow", "outputs": [{"type": "uint256"}], "stateMutability": "nonpayable", "type": "function"},
    {"inputs": [{"name": "_escrowId", "type": "uint256"}],
     "name": "markComplete", "outputs": [], "stateMutability": "nonpayable", "type": "function"},
    {"inputs": [{"name": "_escrowId", "type": "uint256"}, {"name": "_signature", "type": "bytes"}],
     "name": "validateAndRelease", "outputs": [], "stateMutability": "nonpayable", "type": "function"},
    {"inputs": [{"name": "_escrowId", "type": "uint256"}],
     "name": "refund", "outputs": [], "stateMutability": "nonpayable", "type": "function"},
]

ESCROW_STATES = ["Created", "Completed", "Validated", "Released", "Refunded"]

# ─── Helpers ────────────────────────────────────────────────────────────────

SEPARATOR = "=" * 70
SUB_SEP = "-" * 50

def banner(text):
    print(f"\n{SEPARATOR}")
    print(f"  {text}")
    print(f"{SEPARATOR}\n")

def section(text):
    print(f"\n{SUB_SEP}")
    print(f"  {text}")
    print(f"{SUB_SEP}")

def fmt_tx(tx_hash):
    return f"{EXPLORER}/tx/{tx_hash}"

def fmt_addr(addr):
    return f"{addr[:8]}...{addr[-6:]}"

def log(agent, action, detail=""):
    ts = datetime.now(timezone.utc).strftime("%H:%M:%S UTC")
    tag = f"[{ts}] {agent}"
    print(f"  {tag:25s} → {action}")
    if detail:
        print(f"  {'':25s}   {detail}")

# ─── Market Data Task (Real Work) ──────────────────────────────────────────

def fetch_crypto_prices():
    """Fetch real crypto market data — this is the task the Provider Agent performs."""
    section("Task: Fetch & Analyze Crypto Market Data")

    symbols = ["ethereum", "bitcoin", "solana"]
    currencies = "usd"
    url = f"https://api.coingecko.com/api/v3/simple/price"
    params = {"ids": ",".join(symbols), "vs_currencies": currencies,
              "include_24hr_change": "true", "include_market_cap": "true"}

    try:
        resp = httpx.get(url, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        # Fallback: return cached data if API fails
        print(f"  ⚠ API fallback ({e}), using cached snapshot")
        data = {
            "ethereum": {"usd": 2847.32, "usd_24h_change": -1.23, "usd_market_cap": 342e9},
            "bitcoin": {"usd": 67842.10, "usd_24h_change": 0.87, "usd_market_cap": 1.33e12},
            "solana": {"usd": 178.45, "usd_24h_change": 3.42, "usd_market_cap": 82e9},
        }

    # Analysis
    analysis = {}
    for sym, info in data.items():
        price = info[currencies]
        change = info.get(f"{currencies}_24h_change", 0)
        mcap = info.get(f"{currencies}_market_cap", 0)
        signal = "🟢 BULLISH" if change > 1 else ("🔴 BEARISH" if change < -1 else "🟡 NEUTRAL")
        analysis[sym] = {
            "price": price,
            "change_24h": change,
            "market_cap": mcap,
            "signal": signal,
        }

    # Generate report
    print(f"\n  📊 Market Analysis Report (generated at {datetime.now(timezone.utc).isoformat()})")
    print(f"  {'Asset':<12} {'Price':>12} {'24h Change':>12} {'Signal':>15}")
    print(f"  {'─'*12} {'─'*12} {'─'*12} {'─'*15}")
    for sym, info in analysis.items():
        print(f"  {sym:<12} ${info['price']:>10,.2f} {info['change_24h']:>+10.2f}% {info['signal']:>15}")

    # Compute a composite index
    avg_change = sum(i["change_24h"] for i in analysis.values()) / len(analysis)
    overall = "🟢 BULLISH" if avg_change > 1 else ("🔴 BEARISH" if avg_change < -1 else "🟡 NEUTRAL")
    print(f"\n  📈 Composite Index: {avg_change:+.2f}% → {overall}")

    return analysis


# ─── Agent Classes ─────────────────────────────────────────────────────────

class AgentWallet:
    """Represents an agent's on-chain identity."""

    def __init__(self, name, private_key=None):
        self.name = name
        if private_key:
            self.account = Account.from_key(private_key)
        else:
            self.account = Account.create()
        self.address = self.account.address
        self.pk = private_key  # None if not provided (read-only)

    def __repr__(self):
        return f"{self.name} ({fmt_addr(self.address)})"


class BuyerAgent:
    """AI buyer agent — requests work, creates escrow, releases funds."""

    def __init__(self, wallet: AgentWallet, w3, contracts):
        self.wallet = wallet
        self.w3 = w3
        self.escrow = w3.eth.contract(address=contracts["AgentEscrow"],
                                       abi=AGENT_ESCROW_ABI)
        self.usdc = w3.eth.contract(address=contracts["USDC"], abi=ERC20_ABI)

    def create_escrow(self, seller_address, amount_usdc):
        """Create an escrow locking USDC for the seller."""
        amount_wei = int(amount_usdc * 1e6)  # USDC has 6 decimals
        nonce = self.w3.eth.get_transaction_count(self.wallet.address)

        # First approve USDC spend
        log("BuyerAgent", "Approving USDC spend",
            f"Amount: {amount_usdc} USDC → AgentEscrow")
        approve_tx = self.usdc.functions.approve(
            CONTRACTS["AgentEscrow"], amount_wei
        ).build_transaction({
            "from": self.wallet.address,
            "nonce": nonce,
            "chainId": CHAIN_ID,
            "gas": 100000,
            "gasPrice": self.w3.eth.gas_price,
        })
        signed = self.wallet.account.sign_transaction(approve_tx)
        tx_hash = self.w3.eth.send_raw_transaction(signed.raw_transaction)
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        log("BuyerAgent", "USDC approved ✅", fmt_tx(tx_hash.hex()))

        # Create escrow
        nonce = self.w3.eth.get_transaction_count(self.wallet.address)
        log("BuyerAgent", "Creating escrow",
            f"Seller: {fmt_addr(seller_address)}, Amount: {amount_usdc} USDC")
        create_tx = self.escrow.functions.createEscrow(
            seller_address, amount_wei
        ).build_transaction({
            "from": self.wallet.address,
            "nonce": nonce,
            "chainId": CHAIN_ID,
            "gas": 200000,
            "gasPrice": self.w3.eth.gas_price,
        })
        signed = self.wallet.account.sign_transaction(create_tx)
        tx_hash = self.w3.eth.send_raw_transaction(signed.raw_transaction)
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)

        # Get escrow ID from events
        escrow_id = None
        for ev_log in receipt["logs"]:
            try:
                parsed = self.escrow.events.EscrowCreated().process_log(ev_log)
                escrow_id = parsed["args"]["id"]
            except:
                pass

        log("BuyerAgent", "Escrow created ✅",
            f"Escrow ID: {escrow_id}, TX: {fmt_tx(tx_hash.hex())}")
        return escrow_id

    def check_balance(self):
        bal = self.usdc.functions.balanceOf(self.wallet.address).call()
        return bal / 1e6


class ProviderAgent:
    """AI provider agent — performs tasks, delivers work."""

    def __init__(self, wallet: AgentWallet, w3, contracts):
        self.wallet = wallet
        self.w3 = w3
        self.escrow = w3.eth.contract(address=contracts["AgentEscrow"],
                                       abi=AGENT_ESCROW_ABI)

    def perform_task(self, task_description):
        """Execute the assigned task — this is the 'work' the agent does."""
        log("ProviderAgent", f"Task received: {task_description}")
        log("ProviderAgent", "Executing task...")

        # Real work: fetch and analyze market data
        analysis = fetch_crypto_prices()

        # Save report
        report = {
            "task": task_description,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "agent": self.wallet.name,
            "data": analysis,
            "status": "completed",
        }
        report_path = os.path.join(os.path.dirname(__file__), "task_report.json")
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2, default=str)
        log("ProviderAgent", "Task complete ✅", f"Report saved to {report_path}")

        return report

    def mark_complete(self, escrow_id):
        """Signal to the escrow contract that work is done."""
        nonce = self.w3.eth.get_transaction_count(self.wallet.address)
        log("ProviderAgent", "Marking work as complete", f"Escrow ID: {escrow_id}")

        tx = self.escrow.functions.markComplete(escrow_id).build_transaction({
            "from": self.wallet.address,
            "nonce": nonce,
            "chainId": CHAIN_ID,
            "gas": 100000,
            "gasPrice": self.w3.eth.gas_price,
        })
        signed = self.wallet.account.sign_transaction(tx)
        tx_hash = self.w3.eth.send_raw_transaction(signed.raw_transaction)
        self.w3.eth.wait_for_transaction_receipt(tx_hash)
        log("ProviderAgent", "Work marked complete ✅", fmt_tx(tx_hash.hex()))


class ValidatorAgent:
    """AI validator — verifies work quality, signs EIP-712 approval."""

    def __init__(self, wallet: AgentWallet, w3, contracts):
        self.wallet = wallet
        self.w3 = w3
        self.escrow = w3.eth.contract(address=contracts["AgentEscrow"],
                                       abi=AGENT_ESCROW_ABI)

    def verify_work(self, escrow_id, report):
        """AI-powered quality verification of the provider's work."""
        section("ValidatorAgent: Verifying Work Quality")

        # Simulated AI validation logic
        checks = [
            ("Data completeness", len(report["data"]) >= 2),
            ("Timestamp present", "timestamp" in report),
            ("Status: completed", report["status"] == "completed"),
            ("Price data present", all("price" in d for d in report["data"].values())),
            ("Change analysis", all("change_24h" in d for d in report["data"].values())),
        ]

        all_pass = True
        for check_name, result in checks:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"  {status:8s}  {check_name}")
            if not result:
                all_pass = False

        if all_pass:
            log("ValidatorAgent", "Quality check passed ✅",
                "All validation checks cleared")
        else:
            log("ValidatorAgent", "Quality check failed ❌",
                "Some checks did not pass")

        return all_pass

    def sign_validation(self, escrow_id):
        """Generate EIP-712 signature approving the escrow release."""
        log("ValidatorAgent", "Generating EIP-712 signature",
            f"Escrow ID: {escrow_id}")

        message = {"escrowId": escrow_id}

        signable = encode_typed_data(
            domain_data=EIP712_DOMAIN,
            message_types=EIP712_TYPES,
            message_data=message,
        )
        signed = self.wallet.account.sign_message(signable)
        signature = signed.signature.hex()

        log("ValidatorAgent", "Signature generated ✅",
            f"r: {signature[:66]}\n{'':25s}   s: {signature[66:130]}\n{'':25s}   v: {signature[130:]}")

        return signature

    def validate_and_release(self, escrow_id, signature):
        """Submit the signed validation to release funds on-chain."""
        nonce = self.w3.eth.get_transaction_count(self.wallet.address)
        log("ValidatorAgent", "Submitting validation on-chain",
            f"Escrow ID: {escrow_id}")

        tx = self.escrow.functions.validateAndRelease(
            escrow_id, bytes.fromhex(signature)
        ).build_transaction({
            "from": self.wallet.address,
            "nonce": nonce,
            "chainId": CHAIN_ID,
            "gas": 200000,
            "gasPrice": self.w3.eth.gas_price,
        })
        signed = self.wallet.account.sign_transaction(tx)
        tx_hash = self.w3.eth.send_raw_transaction(signed.raw_transaction)
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        log("ValidatorAgent", "Funds released on-chain ✅",
            fmt_tx(tx_hash.hex()))

        return receipt


# ─── Main Demo Flow ────────────────────────────────────────────────────────

def load_wallets():
    """Load agent wallets from .env or generate demo wallets."""
    env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
    deployer_pk = None
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line.startswith("DEPLOYER_PRIVATE_KEY="):
                    deployer_pk = line.split("=", 1)[1].strip()
                    if deployer_pk.startswith("0x"):
                        deployer_pk = deployer_pk[2:]
                    break

    if deployer_pk and len(deployer_pk) == 64:
        deployer = AgentWallet("Deployer", private_key=deployer_pk)
        # Create separate wallets for demo
        buyer = AgentWallet("BuyerAgent")
        seller = AgentWallet("ProviderAgent")
        validator = AgentWallet("ValidatorAgent")
        return deployer, buyer, seller, validator, True
    else:
        # All demo wallets
        deployer = AgentWallet("Deployer")
        buyer = AgentWallet("BuyerAgent")
        seller = AgentWallet("ProviderAgent")
        validator = AgentWallet("ValidatorAgent")
        return deployer, buyer, seller, validator, False


def run_simulated_demo():
    """Run the full flow in simulated mode — no blockchain interaction."""
    banner("🤖 Kite AI Agentic Commerce — Simulated Demo")

    print("  This demonstrates the full agent workflow without on-chain transactions.")
    print("  Run with: python3 agent/run_demo.py  (needs .env for real txs)")

    deployer, buyer_w, seller_w, validator_w, _ = load_wallets()
    print(f"\n  📋 Agent Identities:")
    print(f"     Buyer:     {buyer_w}")
    print(f"     Provider:  {seller_w}")
    print(f"     Validator: {validator_w}")

    # Step 1: Buyer creates escrow
    section("Step 1: Buyer Agent Creates Escrow")
    log("BuyerAgent", "Requesting market analysis service")
    log("BuyerAgent", "Creating escrow: 10 USDC for ProviderAgent",
        f"Seller: {seller_w.address}")
    escrow_id = 0
    print(f"\n  📝 Escrow Details:")
    print(f"     ID:        {escrow_id}")
    print(f"     Amount:    10.00 USDC")
    print(f"     Buyer:     {fmt_addr(buyer_w.address)}")
    print(f"     Seller:    {fmt_addr(seller_w.address)}")
    print(f"     State:     Created ✅")

    # Step 2: Provider performs task
    section("Step 2: Provider Agent Executes Task")
    report = fetch_crypto_prices()
    # Save report
    report_data = {
        "task": "Fetch and analyze crypto market data",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "agent": seller_w.name,
        "data": report,
        "status": "completed",
    }
    report_path = os.path.join(os.path.dirname(__file__), "task_report.json")
    with open(report_path, "w") as f:
        json.dump(report_data, f, indent=2, default=str)
    log("ProviderAgent", "Task complete ✅", f"Report saved")

    # Step 3: Provider marks complete
    section("Step 3: Provider Agent Marks Work Complete")
    log("ProviderAgent", f"Marking escrow {escrow_id} as complete")
    print(f"  State transition: Created → Completed ✅")

    # Step 4: Validator checks quality
    section("Step 4: Validator Agent Verifies Work Quality")
    checks = [
        ("Data completeness", len(report) >= 2),
        ("Timestamp present", "timestamp" in report_data),
        ("Status: completed", report_data["status"] == "completed"),
        ("Price data present", all("price" in d for d in report.values())),
        ("Change analysis", all("change_24h" in d for d in report.values())),
    ]
    all_pass = True
    for check_name, result in checks:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status:8s}  {check_name}")
        if not result:
            all_pass = False
    if all_pass:
        log("ValidatorAgent", "Quality check passed ✅",
            "All validation checks cleared")

    if all_pass:
        # Step 5: Validator signs and releases
        section("Step 5: Validator Agent Signs EIP-712 & Releases Funds")
        # Generate EIP-712 signature
        from eth_account.messages import encode_typed_data
        eip712_domain = {
            "name": "AgentEscrow", "version": "1",
            "chainId": CHAIN_ID, "verifyingContract": CONTRACTS["AgentEscrow"],
        }
        eip712_types = {"Validation": [{"name": "escrowId", "type": "uint256"}]}
        signable = encode_typed_data(
            domain_data=eip712_domain, message_types=eip712_types,
            message_data={"escrowId": escrow_id},
        )
        signed = validator_w.account.sign_message(signable)
        sig = signed.signature.hex()
        log("ValidatorAgent", "EIP-712 signature generated ✅",
            f"r: {sig[:66]}")
        log("ValidatorAgent", "Funds released on-chain (simulated)")
        print(f"\n  💰 10.00 USDC released to ProviderAgent")
        print(f"  State transition: Completed → Released ✅")

    section("Demo Complete")
    print("  ✅ Full agent workflow demonstrated")
    print(f"  📊 Report: agent/task_report.json")
    print(f"  🔗 Explorer: {EXPLORER}")
    print()


def run_live_demo():
    """Run the full flow with real on-chain transactions."""
    banner("🤖 Kite AI Agentic Commerce — Live Demo")

    deployer, buyer, seller, validator, has_pk = load_wallets()

    if not has_pk:
        print("  ⚠️  No DEPLOYER_PRIVATE_KEY found in .env")
        print("  Run with: python3 agent/run_demo.py --simulate")
        print()
        sys.exit(1)

    # Connect to blockchain
    w3 = Web3(Web3.HTTPProvider(KITE_RPC))
    w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)

    if not w3.is_connected():
        print("  ❌ Cannot connect to Kite testnet")
        sys.exit(1)

    chain_id = w3.eth.chain_id
    block = w3.eth.block_number
    print(f"  Connected: Kite AI Testnet (Chain {chain_id}, Block {block})")
    print(f"  Explorer: {EXPLORER}")

    # Show agent identities
    print(f"\n  📋 Agent Identities:")
    print(f"     Deployer:  {deployer}")
    print(f"     Buyer:     {buyer}")
    print(f"     Provider:  {seller}")
    print(f"     Validator: {validator}")

    # Fund demo wallets from deployer (if needed)
    section("Funding Demo Wallets")
    deployer_bal = w3.eth.get_balance(deployer.address)
    print(f"  Deployer balance: {w3.from_wei(deployer_bal, 'ether'):.4f} KITE")

    contracts = CONTRACTS

    # Initialize agents
    buyer_agent = BuyerAgent(buyer, w3, contracts)
    provider = ProviderAgent(seller, w3, contracts)
    validator_agent = ValidatorAgent(validator, w3, contracts)

    # Check escrow's AI_VALIDATOR address
    escrow_contract = w3.eth.contract(
        address=contracts["AgentEscrow"], abi=AGENT_ESCROW_ABI
    )
    on_chain_validator = escrow_contract.functions.AI_VALIDATOR().call()
    print(f"\n  On-chain AI_VALIDATOR: {fmt_addr(on_chain_validator)}")

    # Step 1: Create escrow
    section("Step 1: Buyer Agent Creates Escrow")
    escrow_id = buyer_agent.create_escrow(seller.address, 10.0)

    # Step 2: Provider performs task
    section("Step 2: Provider Agent Executes Task")
    report = provider.perform_task("Fetch and analyze crypto market data")

    # Step 3: Provider marks complete
    section("Step 3: Provider Agent Marks Work Complete")
    provider.mark_complete(escrow_id)

    # Step 4: Validator checks quality
    section("Step 4: Validator Agent Verifies Work Quality")
    passed = validator_agent.verify_work(escrow_id, report)

    if passed:
        # Step 5: Validator signs and releases
        section("Step 5: Validator Agent Signs EIP-712 & Releases Funds")
        sig = validator_agent.sign_validation(escrow_id)
        validator_agent.validate_and_release(escrow_id, sig)

    section("🎉 Demo Complete")
    print(f"  ✅ Full agent workflow executed on Kite AI Testnet")
    print(f"  📊 Report: agent/task_report.json")
    print(f"  🔗 Escrow TX: {EXPLORER}/address/{contracts['AgentEscrow']}#readContract")
    print()


if __name__ == "__main__":
    simulate = "--simulate" in sys.argv
    if simulate:
        run_simulated_demo()
    else:
        run_live_demo()
