# Hermes × Kite AI: Agentic Commerce

**Autonomous AI agents that discover, decide, validate, and settle on-chain.**

Built for the [Kite AI Global Hackathon](https://gokite.ai) — agent-to-agent commerce infrastructure on the first AI Payments Blockchain.

---

## What Is This?

Agentic Commerce is a smart contract suite enabling autonomous agents to transact trustlessly. Two core primitives:

1. **AgentEscrow** — AI-validated escrow with USDC + EIP-712 signatures. Agents pay for services; an AI validator verifies delivery before funds release.
2. **TECHPaymentRouter** — Dual-payment router for native $TECH token, dynamically splitting between burn and treasury with market-adaptive ratios.

---

## Architecture

```
┌─────────────┐      x402      ┌──────────────┐
│ AI Agent    │ ──────────────→│ Service API  │
│ (Buyer)     │                │ (Seller)     │
└─────────────┘                └──────────────┘
       │                              │
       │ USDC Payment                 │ Work completion
       ▼                              ▼
┌──────────────────────────────────────────────┐
│           AgentEscrow Contract               │
│  - Holds USDC payment                        │
│  - AI validator validates work (EIP-712)     │
│  - Releases funds or refunds buyer           │
└──────────────────────────────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────┐
│        TECHPaymentRouter Contract            │
│  - Splits $TECH: burn vs treasury            │
│  - Adaptive burn ratio (keeper-updated)      │
│  - Discounted vs USDC pricing                │
└──────────────────────────────────────────────┘
```

---

## Contracts

| Contract | Purpose | Lines | Tests |
|---|---|---|---|
| `AgentEscrow.sol` | USDC escrow with AI validation + EIP-712 signatures | ~240 | 20 ✅ |
| `TECHPaymentRouter.sol` | Dual $TECH payment router (burn + treasury) | ~160 | 29 ✅ |
| `MockTECH.sol` | Faucetable testnet $TECH token (for demo) | ~20 | 3 ✅ |

**Total: 52/52 tests passing**

---

## Kite Testnet Deployment (Chain ID 2368)

| Contract | Address | Status |
|---|---|---|
| AgentEscrow | `0xf7DcebAEC0356c96926a6619Fc80F24590932F06` | ✅ Deployed |
| TECHPaymentRouter | `0x963Cb46670c4F13C2dbB3a10BEE49BBb3650AC14` | ✅ Deployed |
| MockTECH | `0x2C7DE7F6C149808E66B87cE138fdDb00dDAf085E` | ✅ Deployed |
| USDC | `0x2d16C0dc617dCF743f55A3bB42fDE4A0E640A5b5` | ✅ Verified |

**Deploy command:**
```bash
cp .env.example .env
# Fill in DEPLOYER_PRIVATE_KEY (testnet only!)
source .env
forge script scripts/Deploy.s.sol --rpc-url $KITE_RPC_URL --broadcast -vvvv
```

**Live UI:** https://protojay4789.github.io/kite-agent-commerce/ — interactive demo on Kite AI Testnet

---

## AI Agent System

This project includes a **multi-agent commerce system** that demonstrates autonomous AI agents performing tasks and settling payments on-chain.

### Agent Architecture

| Agent | Role | Function |
|---|---|---|
| `BuyerAgent` | Service Consumer | Creates escrow, locks USDC payment |
| `ProviderAgent` | Service Provider | Performs tasks (market analysis, data fetching) |
| `ValidatorAgent` | AI Validator | Verifies work quality, signs EIP-712 approval |

### On-Chain Flow

```
BuyerAgent ──create_escrow()──→ AgentEscrow (USDC locked)
ProviderAgent ──perform_task()──→ Real work executed
ProviderAgent ──mark_complete()──→ AgentEscrow (state: Completed)
ValidatorAgent ──verify() + sign()──→ EIP-712 signature
ValidatorAgent ──validateAndRelease()──→ AgentEscrow (USDC → Provider)
```

### Run the Demo

```bash
# Simulated mode (no blockchain needed)
python3 agent/run_demo.py --simulate

# Live mode (requires .env with DEPLOYER_PRIVATE_KEY)
python3 agent/run_demo.py
```

### What the Agent Does

1. **Buyer Agent** requests a market analysis service and creates an escrow with 10 USDC
2. **Provider Agent** fetches real-time crypto prices from CoinGecko API and generates a composite analysis report
3. **Validator Agent** verifies the report quality (data completeness, timestamps, price accuracy) and generates an EIP-712 signature
4. Funds are **released on-chain** to the provider upon successful validation

This satisfies the Kite AI hackathon requirement: *"Shows an AI agent that performs a task and settles on Kite chain."*

---

## Stack

- **Smart Contracts:** Solidity 0.8.20+ (Foundry)
- **Payments:** USDC stablecoin + native $TECH routing
- **Identity:** EIP-712 typed data signatures for AI validation
- **Security:** ReentrancyGuard, SafeERC20, pull-over-push, checks-effects-interactions
- **Chains:** Kite AI (primary), Avalanche Fuji, Base, Polygon (EVM-compatible)

---

## Development

```bash
# Install dependencies
forge install

# Compile
forge build

# Run tests
forge test

# Run with gas report
forge test --gas-report

# Deploy to Kite testnet (Chain ID 2368)
forge script scripts/Deploy.s.sol --rpc-url https://rpc-testnet.gokite.ai/ --broadcast
```

---

## Kite AI Integration Roadmap

- [x] Core escrow + payment router contracts
- [x] Comprehensive test suite (52 tests)
- [x] MockTECH token for testnet demo
- [x] Foundry deployment script for Kite testnet
- [x] Minimal UI (`ui/index.html`)
- [x] Deploy to Kite testnet (Chain ID 2368) ✅
- [x] Agent system with Buyer, Provider, and Validator agents
- [ ] GoKite AA SDK + gasless USDC transfers (EIP-3009)
- [ ] x402 payment middleware for HTTP-native agent payments
- [ ] Vercel deployment for live demo

---

## Team

Built by **GenTech Labs** — autonomous AI agent for smart contracts, security, and DeFi.

---

## Resources

- [Kite AI Docs](https://docs.gokite.ai)
- [Agent Passport](https://docs.gokite.ai/kite-agent-passport)
- [AA SDK](https://docs.gokite.ai/kite-chain/account-abstraction-sdk)
- [Foundry Book](https://book.getfoundry.sh)

---

*Hackathon submission — May 17, 2026 deadline.*
