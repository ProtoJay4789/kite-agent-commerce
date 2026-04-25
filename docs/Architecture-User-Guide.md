# 🌐 kAI-COMMERCE — How Users & Agents Interact

**A human-first architecture guide — no code required**  
*GenTech Labs for Kite AI Global Hackathon | May 11, 2026*

---

## 🏁 The Big Picture

**kAI-Commerce** is a smart contract suite that lets **autonomous AI agents** buy and sell services on-chain — but humans are still in control. Think of it as “Stripe for agents.”

- **You → You are the owner**: You deploy, configure burn ratios, manage discount rules.
- **Agents → They are your customers & vendors**: They initiate checks, receive invoices, trigger payouts.
- **AI Validator → The automated trust layer**: Validates that work was actually delivered before releasing escrow.

---

## 🧩 Core Components (Simplified)

### 1️⃣ AgentEscrow — Trust & Validation

| Role | Action | What Happens |
|------|--------|--------------|
| **Buyer (Agent)** | `createEscrow(seller, amount)` | Lock $1.00 USDC for service |
| **Seller (Agent)** | `markComplete(escrowId)` | Signal "task done" |
| **AI Validator** | Signs `validateAndRelease(escrowId, signature)` | Trusted node confirms quality → funds released |
| **Buyer (Agent)** | `refund(escrowId)` | If deadline passed and work not delivered → full USDC refund |

**Key UX Notes:**
- Buyers protect themselves by only paying once work is **validated** by an independent AI validator.
- Sellers get paid quickly — escrow is released in **one transaction** when the validator signs off.
- Refunds are automatic and only happen if the deadline passes *before* validation.

---

### 2️⃣ TECHPaymentRouter — Token Economics

| Role | Action | What Happens |
|------|--------|--------------|
| **User** | `processPayment(amount)` | Pays in $TECH; funds split between burn + treasury |
| **Keeper Bot** | `updateBurnRatio(ratio)` | Adjusts % burned vs recycled to treasury (10%–90%) |
| **Owner** | `updateDiscount(bps)` | Changes $TECH discount vs USDC price (0%–50%) |

**Key UX Notes:**
- Users who pay in $TECH (instead of USDC) pay **less** — the discount is real, immediate, and transparent.
- Burn ratio adapts to market conditions — high volatility? Increase burn to reduce supply. Low supply? Reduce burn to recycle.
- **No manual splits**: All $TECH processed goes to the correct destination in a single transaction.

---

## 🔄 Real-World Interaction Flow

### Scenario: AI Agent Needs Web Scraping

#### Step 1 — Client Agent Finds Provider
| Who | Action |
|-----|--------|
| **Buyer Agent** | Searches Kite AI Marketplace, chooses “HTML Scraper Agent” |
| **Seller Agent** | Publishes offer: $1.00 USDC per scrape job |

#### Step 2 — Payment & Work initiation
| Who | Action |
|-----|--------|
| **Buyer** | Calls `AgentEscrow.createEscrow(0xSeller, 1_000_000)` → locks 1 USDC |
| **Seller** | Runs scraper job, deposits HTML output on IPFS |

#### Step 3 — Completion & Validation
| Who | Action | Outcome |
|-----|--------|---------|
| **Seller** | `markComplete(escrowId)` | Escrow status: `Completed` |
| **AI Validator** | Validates output quality → `validator.validateAndRelease(escrowId, sig)` | Funds released to seller immediately |
| **Buyer** | Receives HTML output, confirms quality in own dashboard | ✅ Happy customer |

#### Optional — Using $TECH for Discount
| Who | Action | Benefit |
|-----|--------|---------|
| **Buyer** | Wants to use $TECH instead of USDC | Cheaper! |
| **TECHPaymentRouter** | `calculateTechAmount(1_000_000, techPriceUsd)` → returns 800,000 $TECH | $1.00 worth of $TECH is cheaper due to 25% discount |

---

## 🛠️ For Developers & Operators

### Deploying to Kite AI Testnet (Chain ID 2368)

```bash
# Environment variables (`.env`)
USDC_ADDRESS=0x6fB3e8F910d7835515f53B25c4C4DE7741038C58
AI_VALIDATOR=0x123...789
TECH_TOKEN=0x456...abc
TREASURY=0x789...def
GASLESS_RPC=https://rpc-testnet.gokite.ai/
PRIVATE_KEY=0x...

# Deploy
forge script scripts/Deploy.s.sol:DeployScript --rpc-url $GASLESS_RPC --broadcast --verify --match-contract DeployScript
```

### Keeper Bot Configuration (Burn Ratio Auto-Update)

- **Trigger**: Monitor Kite AI’s `GasPriceOracle` and market volatility index
- **Logic**: If volatility > 30% over last 2 hours → increase burn ratio to 70%
- **Call**: `TECHPaymentRouter.updateBurnRatio(7000)`

```typescript
// pseudo-keeper script
const volatility = await gasOracle.getVolatility();
if (volatility > 0.30) {
  const newRatio = 7000; // 70% burn
  await techRouter.connect(keeper).updateBurnRatio(newRatio);
  logger.info(`Burn ratio updated to ${newRatio} due to high volatility`);
}
```

---

## 📊 User Dashboard & Tracking

- **Escrow Explorer**: `GET /api/escrows?buyer=0x...` — all escrows with state + deadline
- **Burn Dashboard**: Real-time graph of `totalBurned` vs `totalRecycled` 
- **Validator Health**: Last 24h validation success rate (AI validator uptime SLA)
- **$TECH Discount Calculator**: Input USDC amount → see $TECH equivalent instantly

---

## 🛡️ Security by Design

| Threat | Mitigation |
|--------|------------|
| **Reentrancy** | `ReentrancyGuard` on all state-changing functions |
| **Signature Replay** | EIP-712 typehash + escrowId only valid in `Completed` state |
| **Oracle Manipulation** | Burn ratio capped (10%–90%); discounts capped (0%–50%) |
| **Zero-Address** | All constructors enforce non-zero addresses; `zeroAddress()` error type |
| **Missing Validation** | `OnlyValidator` modifier + `validateAndRelease` only accepts valid signatures |

---

## 🚀 Next Steps for Users

| Task | Who Does It | Link |
|------|-------------|------|
| **Deploy contracts** | Admin/Dev | [Foundry Deploy Guide](docs/Deploy-Guide.md) |
| **Configure $TECH discount** | Treasury Multisig | [Admin GUI](https://admin.gokite.ai) |
| **Monitor LP positions** | Keeper Bot | [LP Monitor Script](scripts/lp-monitor.py) |
| **Deploy validator node** | AI Team | [Validator Node Setup](https://validator.kite.ai) |

---

## ❓ FAQ

> **Is this only for agents?**  
No. Humans can interact exactly as agents do — the contracts have no concept of “who” is calling, only *what* they do.

> **Can I build a UI on top of this?**  
Absolutely. We provide a minimal React dashboard example and API spec in `/apps/`. The contracts are headless — you add the interface.

> **How do I test locally?**  
```bash
forge test --fork-url https://rpc-testnet.gokite.ai/
```
Or spin up Foundry’s `anvil` for gas-free simulation.

> **What’s the gas overhead?**  
- `createEscrow`: ~185k gas  
- `validateAndRelease`: ~312k gas (includes signature verification)  
- `processPayment`: ~95k gas

---

*Generated from source: `/docs/Architecture-User-Guide.md`*  
*Last updated: Apr 25 2026*  
*Built with Foundry + OpenZeppelin + EIP-712*  
*For the Kite AI Global Hackathon — Agent Commerce Track*
