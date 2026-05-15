# Kite AI Demo Video Script

**Target length:** 2:30-3:00 minutes
**Recording tool:** OBS Studio or Win+G (Windows Game Bar)
**What to show on screen:** Browser with GitHub Pages UI + block explorer + agent terminal

---

## [0:00–0:15] Hook

> "What happens when AI agents need to pay each other for services? Today, I'll show you Agentic Commerce — autonomous agents performing real work and settling payments on Kite AI, using AI-validated escrow smart contracts."

## [0:15–0:45] Problem

> "Right now, AI agents can't transact trustlessly. If Agent A pays Agent B for an API call or data service, there's no guarantee the work gets done. We built an escrow system where an AI validator verifies the work before funds are released — all on-chain."

## [0:45–1:30] Demo — UI + Escrow Creation

> "Here's the live UI on Kite AI testnet. Three contracts are deployed: AgentEscrow, TECHPaymentRouter, and MockTECH.
>
> Watch as the Buyer Agent creates an escrow — it locks 10 USDC into the smart contract. The funds are held until an AI validator confirms the work is done.
>
> [Show the UI creating an escrow, or show the agent terminal output]"

## [1:30–2:00] Demo — Agent Task + Validation

> "The Provider Agent then performs the actual task — fetching real-time crypto market data from CoinGecko and generating an analysis report.
>
> The AI Validator Agent reviews the output: checking data completeness, timestamp accuracy, and price validity. Once all checks pass, it signs an EIP-712 typed data signature.
>
> [Show the agent terminal output with the validation checks passing]"

## [2:00–2:30] Demo — On-Chain Settlement

> "That signature is submitted on-chain — funds are released from escrow to the provider. No human involvement. The entire flow is automated: task request → execution → verification → payment.
>
> [Show the transaction on the Kite block explorer]"

## [2:30–2:50] Architecture

> "Three Solidity contracts: AgentEscrow handles USDC escrow with AI validation, TECHPaymentRouter splits native token payments between burn and treasury, and MockTECH is our testnet token. 52 tests passing, full ReentrancyGuard and EIP-712 security."

## [2:50–3:00] Close

> "Agentic Commerce — where AI agents discover, decide, validate, and settle on-chain. Built by GenTech Labs for the Kite AI Global Hackathon. Code is on GitHub."

---

## What to Show on Screen (Recording Order)

1. **GitHub repo page** — https://github.com/ProtoJay4789/kite-agent-commerce
   - Show README with contract addresses, agent architecture diagram
   - Show 52/52 tests passing section

2. **Live UI** — https://protojay4789.github.io/kite-agent-commerce/
   - Show the deployed contract addresses
   - Show the create escrow interface

3. **Agent terminal** — `python3 agent/run_demo.py --simulate`
   - Show the full agent workflow output
   - Highlight the EIP-712 signature generation
   - Show the market analysis report

4. **Block explorer** — https://testnet.kitescan.ai/
   - Show the deployed AgentEscrow contract
   - Show a transaction (escrow creation or release)
   - Show the contract verified code

5. **Agent source code** — agent/run_demo.py
   - Briefly show the BuyerAgent, ProviderAgent, ValidatorAgent classes
   - Show the EIP-712 signing logic

## Tips for Recording

- Keep your mouse movements smooth — don't rush
- Pause briefly after each major section
- Speak clearly, at a medium pace
- Don't read the script verbatim — use it as a guide
- Total time should be 2:30-3:00 minutes max
- Judges want to see it WORK, not hear a lecture
