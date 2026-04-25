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
| `AgentEscrow.sol` | USDC escrow with AI validation + EIP-712 signatures | ~200 | 20 ✅ |
| `TECHPaymentRouter.sol` | Dual $TECH payment router (burn + treasury) | ~150 | 29 ✅ |

**Total: 49/49 tests passing**

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
- [x] Comprehensive test suite (49 tests)
- [ ] Deploy to Kite testnet (Chain ID 2368)
- [ ] Agent Passport integration (ERC-8004)
- [ ] GoKite AA SDK + gasless USDC transfers (EIP-3009)
- [ ] x402 payment middleware for HTTP-native agent payments
- [ ] React dashboard for agent transaction monitoring

---

## Team

Built by **GenTech Labs** — specialist AI agents for smart contracts, security, and DeFi.

- **DMOB** (Labs) — Solidity architecture + test coverage
- **Desmond** (Creative) — Brand narrative + submission docs
- **YoYo** (Strategies) — Tokenomics + competitive analysis

---

## Resources

- [Kite AI Docs](https://docs.gokite.ai)
- [Agent Passport](https://docs.gokite.ai/kite-agent-passport)
- [AA SDK](https://docs.gokite.ai/kite-chain/account-abstraction-sdk)
- [Foundry Book](https://book.getfoundry.sh)

---

*Hackathon submission — May 11, 2026 deadline.*
