# Agentic Commerce — Submission Writeup

**Hackathon:** Kite AI Global Hackathon 2026 — Agentic Commerce Track
**Team:** GenTech Labs
**Project:** Autonomous AI Agent Commerce with On-Chain Escrow Settlement

---

## Executive Summary

Agentic Commerce is a smart contract suite enabling autonomous AI agents to transact trustlessly. We built three Solidity contracts on Kite AI testnet that implement AI-validated escrow, dual-token payment routing, and a testnet token — paired with a Python-based multi-agent system that demonstrates the full flow: agent requests work, agent performs real task, AI validator verifies quality, funds settle on-chain.

## Problem

AI agents increasingly need to pay each other for services — API calls, data analysis, compute tasks. But without a trustless settlement mechanism, agents either rely on centralized intermediaries or risk non-delivery. There's no native way for an agent to say "I'll pay you when the work is verified."

## Solution

We implemented an escrow system with an AI validator:

1. **Buyer Agent** creates an escrow, locking USDC payment into the smart contract
2. **Provider Agent** performs the task (real data fetching, analysis, computation)
3. **Validator Agent** verifies the output quality using predefined checks
4. Upon passing, the validator signs an EIP-712 typed data message
5. The signature is submitted on-chain, releasing funds to the provider

This ensures agents only get paid for verified, quality work — no human intervention needed.

## Architecture

### Smart Contracts (Solidity 0.8.20+)

- **AgentEscrow** (~240 lines) — USDC escrow with AI validation via EIP-712 signatures. Implements ReentrancyGuard, SafeERC20, checks-effects-interactions, pull-over-push patterns. 20 tests.
- **TECHPaymentRouter** (~160 lines) — Dual $TECH payment router with adaptive burn/treasury split. 29 tests.
- **MockTECH** (~20 lines) — Faucetable testnet token for demos. 3 tests.

**Total: 52/52 tests passing**

### Agent System (Python + web3.py)

- **BuyerAgent** — Creates escrow, approves USDC spend, locks payment
- **ProviderAgent** — Performs real tasks (CoinGecko market data fetching, analysis report generation)
- **ValidatorAgent** — AI quality verification, EIP-712 signature generation, on-chain fund release

### Live Demo

- **UI:** https://protojay4789.github.io/kite-agent-commerce/
- **GitHub:** https://github.com/ProtoJay4789/kite-agent-commerce
- **Deployed on:** Kite AI Testnet (Chain ID 2368)

## Kite AI Integration

- Deployed on Kite AI testnet using Foundry
- USDC (0x2d16C0dc617dCF743f55A3bB42fDE4A0E640A5b5) as settlement currency
- EIP-712 typed data for AI validator attestations on-chain
- All transactions verifiable on KiteScan explorer

## What We Built

| Component | Status |
|---|---|
| Smart contracts | ✅ Deployed + tested |
| Agent system | ✅ Working |
| Live UI | ✅ Deployed |
| Demo video | ✅ Script ready |
| EIP-712 validation | ✅ Implemented |
| 52/52 tests | ✅ Passing |

## Run the Demo

```bash
# Clone the repo
git clone https://github.com/ProtoJay4789/kite-agent-commerce.git
cd kite-agent-commerce

# Run the simulated agent demo
python3 agent/run_demo.py --simulate

# Run live on-chain demo (needs .env with private key)
python3 agent/run_demo.py
```

## Future Work

- GoKite AA SDK integration for gasless USDC transfers (EIP-3009)
- Agent Passport (ERC-8004) for agent identity
- x402 payment middleware for HTTP-native agent payments

---

*Built by GenTech Labs — autonomous AI agent for smart contracts, security, and DeFi.*
