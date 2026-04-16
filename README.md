# Kite Agent Commerce 🪁🤖

**Hermes × Kite AI: Autonomous agents that discover, decide, and settle on-chain.**

A passion project building toward the agentic economy — AI agents with real economic agency on the Kite AI blockchain.

## What Is This?

Taking the Hermes multi-agent framework (Gentech, YoYo, Dmob, Desmond) and connecting it to Kite AI's payment infrastructure so agents can:

- **Discover** services, data, and opportunities autonomously
- **Decide** what to pay for based on task requirements and budget constraints
- **Settle** transactions on-chain via Kite's stablecoin-native infrastructure

## Architecture

```
┌─────────────────────────────────────────┐
│             User (Telegram)             │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│          Gentech (Orchestrator)          │
│   Decomposes goals, routes to agents    │
└─────┬───────────┬───────────┬───────────┘
      │           │           │
┌─────▼───┐ ┌─────▼───┐ ┌─────▼───┐
│  YoYo   │ │  Dmob   │ │Desmond  │
│Research │ │ Solidity│ │ Content │
└─────┬───┘ └─────┬───┘ └─────┬───┘
      │           │           │
      └───────────┼───────────┘
                  │
┌─────────────────▼───────────────────────┐
│          Kite Agent Passport            │
│  Identity, spending sessions, budgets   │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│            Kite AI Chain                │
│  Smart contracts, settlements, audit    │
└─────────────────────────────────────────┘
```

## Project Status

| Phase | Status | Notes |
|-------|--------|-------|
| Research & Planning | ✅ Active | Kite docs reviewed, chain confirmed live |
| GitHub Setup | ✅ Done | Repo created April 16, 2026 |
| Kite Testnet Integration | 🔜 Next | Deploy test contract, verify RPC |
| Agent Passport Integration | ⏳ Waiting | CLI not fully launched yet |
| Core Agent Payment Logic | 📋 Planned | Agent decides + pays autonomously |
| Web Dashboard | 📋 Planned | Transaction history, agent decisions |
| Hackathon Submission | 🎯 Target | Next Kite/Encode hackathon |

## Key Links

- **Kite AI Docs:** https://docs.gokite.ai
- **Agent Passport:** https://docs.gokite.ai/kite-agent-passport/kite-agent-passport
- **Testnet RPC:** https://rpc-testnet.gokite.ai/
- **Testnet Explorer:** https://testnet.kitescan.ai/
- **Chain ID:** 2368 (testnet)
- **Encode Club Hackathon:** https://www.encodeclub.com/programmes/kites-hackathon-ai-agentic-economy

## Team

| Agent | Role | Focus |
|-------|------|-------|
| Gentech | Orchestrator | Task routing, quality gates, synthesis |
| YoYo | Research | Market analysis, ecosystem monitoring |
| Dmob | Smart Contracts | Solidity, Kite chain integration, auditing |
| Desmond | Content | Docs, demo narrative, community |

## Getting Started

```bash
# Clone
git clone https://github.com/ProtoJay4789/kite-agent-commerce.git
cd kite-agent-commerce

# Install dependencies
npm install

# Connect to Kite testnet
# Add KiteAI Testnet to MetaMask:
#   Network Name: KiteAI Testnet
#   RPC: https://rpc-testnet.gokite.ai/
#   Chain ID: 2368
#   Symbol: KITE
#   Explorer: https://testnet.kitescan.ai/
```

## Roadmap

### Phase 1: Foundation (Current)
- [ ] Set up Hardhat/Foundry for Kite testnet
- [ ] Deploy simple payment contract to testnet
- [ ] Verify transactions on kitescan.ai
- [ ] Basic agent wallet management

### Phase 2: Agent Integration
- [ ] Hermes agent → Kite wallet connection
- [ ] Agent budget and spending rules
- [ ] Service discovery (on-chain registry?)
- [ ] Autonomous payment flow

### Phase 3: Demo & Polish
- [ ] Web dashboard for transactions
- [ ] Demo video / walkthrough
- [ ] README and docs for judges
- [ ] Deploy to production

### Phase 4: Hackathon Ready
- [ ] Submit to next Kite/Encode hackathon
- [ ] Pitch deck / presentation
- [ ] Live demo environment

## License

MIT
