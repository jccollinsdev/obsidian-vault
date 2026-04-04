# Thesis: EWY — Institutional Research Report
## iShares MSCI South Korea ETF (EWY)

**Date:** April 4, 2026
**Current Price:** $122.87
**52-Week High:** $154.22 | **52-Week Low:** $48.49
**ETF P/E (TTM):** 16.5x
**Position:** RESEARCH — NOT ENTERED
**Analyst:** Josiah Collins

---

## Executive Summary

**Rating: SPECULATIVE BUY — 12-month thesis**

Samsung Electronics (22.35% of EWY) and SK Hynix (18.78%) together comprise **41.1% of the fund**. These are not just holdings — they are the thesis. And the thesis is this: the market is underpricing how long and how deep the AI memory supercycle runs.

Agentic AI doesn't just use more compute — it creates a structurally different memory demand profile. One "prompt" in an agentic system can trigger 10–15 sequential reasoning steps, each requiring memory bandwidth to load context, retrieve tools, and write outputs. The memory wall isn't a bottleneck that gets solved — it's a permanent architectural constraint that gets worse as AI systems scale. HBM and high-density server DRAM become more valuable, not less.

Samsung and SK Hynix control **~90% of global HBM production**. Supply cannot respond quickly. SK Hynix is running fabs at maximum utilization. Samsung just posted record memory revenue in Q4 2025. Server DRAM contract prices have risen **60–70%** from prior周期的 lows. This is not a V-shaped recovery — it is a structural shift in the memory industry.

EWY sits at **$122.87, ~20% below its 52-week high** of $154.22. The market is applying a cycle-peak discount to companies reporting record earnings. That gap is the opportunity.

**12-Month Base Case: $145–155 (+18–26%)**
**Bull Case: $165–175 (+34–42%) — if AI infrastructure spending accelerates through 2026**
**Bear Case: $100–108 (-12–19%) — if memory cycle peaks early or geopolitical risk materializes**

---

## Consistency Check Results

| # | Assumption | Status |
|---|-----------|--------|
| 1 | Agentic AI drives 10–15x more memory per task | Defensible — agentic loops require persistent context and multi-step retrieval, not single inference calls |
| 2 | HBM supply cannot respond fast enough | Confirmed — Samsung and SK Hynix are capacity-constrained; new fabs take 2–3 years |
| 3 | Samsung + SK Hynix = 41% of EWY | Confirmed — stockanalysis.com data: Samsung 22.35%, SK Hynix 18.78% |
| 4 | Oil price headwind is overstated for these companies | Qualified — true for exporters, but oil → KRW weakness is a secondary risk |
| 5 | Forward PEs of 4–6x are artificially depressed | Defensible — investors price a cyclical peak; if cycle extends, re-rating to 8–10x is likely |
| 6 | EWY at $122 represents a pullback entry | Confirmed — 20% below 52w high with fundamentals accelerating |

**Consistency Status: ALL CHECKS PASS — with noted risks**

---

## Step 1 — Data Pull

### Market Data (April 4, 2026)

| Metric | Value |
|--------|-------|
| EWY Price | $122.87 |
| EWY 52w High | $154.22 |
| EWY 52w Low | $48.49 |
| USD/KRW | 1,510.54 KRW/USD |
| Crude Oil (CL=F) | $112.06/bbl |
| Oil 52w High | $119.48 |
| Oil 52w Low | $54.98 |
| S&P 500 (SPY) | yfinance available |
| GDX 3-mo Return | +6.9% |
| EWY 3-mo Return | +17.2% |

### SK Hynix (000660.KS) — Key Holdings

| Metric | Value |
|--------|-------|
| Price | ₩876,000 |
| 52w High | ₩1,099,000 |
| 52w Low | ₩162,700 |
| Down from High | -20.3% |
| Forward P/E | ~4.4x (vs. 52w avg ~8x) |
| EPS (Current Year) | ₩200,732 |
| Revenue Growth (YoY) | +66.1% |
| Earnings Growth (QoQ) | +90.2% |
| Profit Margin | 44.2% |
| Gross Margin | 60.4% |
| Operating Margin | 58.4% |
| Return on Equity | 44.1% |
| Analyst Recommendation | STRONG BUY (1.46/5) |
| Target Mean Price | ₩1,332,730 (+52% upside) |
| Beta | 1.75 |

### Samsung Electronics (005930.KS) — Key Holdings

| Metric | Value |
|--------|-------|
| Price | ₩186,200 |
| 52w High | ₩223,000 |
| 52w Low | ₩52,900 |
| Down from High | -16.5% |
| Forward P/E | ~6.5x |
| EPS (TTM annualized) | ~₩2,909 |
| Revenue Growth (YoY) | +23.8% |
| Earnings Growth (QoQ) | +155.4% |
| Profit Margin | 13.3% |
| Gross Margin | 39.4% |
| Operating Margin | 21.3% |
| Return on Equity | 10.8% |
| Target Mean Price | ₩239,873 (+29% upside) |
| Beta | 1.21 |

### EWY Top 5 Holdings (April 2025)

| Rank | Company | Weight |
|------|---------|--------|
| 1 | Samsung Electronics | 22.35% |
| 2 | SK Hynix | 18.78% |
| 3 | Hyundai Motor | 2.66% |
| 4 | KB Financial Group | 2.32% |
| 5 | SK Square | 2.03% |

Samsung + SK Hynix = **41.13%** of fund. Concentration risk — but also concentration opportunity if thesis plays out.

---

## Step 2 — HBM Market Analysis

### The Memory Wall Is Getting Worse, Not Better

The fundamental thesis rests on a structural imbalance in AI computing: **AI chip compute grows 3x every 2 years, but memory bandwidth only grows 1.6x**. This is the "Memory Wall" problem. As compute density increases, more of a GPU's time is spent waiting for data than executing calculations.

HBM (High Bandwidth Memory) is the solution. It stacks DRAM dies vertically and places them adjacent to the compute chip, dramatically reducing latency and dramatically increasing bandwidth. But HBM is expensive, capacity-constrained, and technically difficult to manufacture — only Samsung and SK Hynix (plus Micron) can produce HBM3E at scale.

### Agentic AI Changes the Math

Current LLMs: 1 prompt → 1 response → memory freed

Agentic AI: 1 task → 10–100 reasoning steps → persistent KV cache → memory held across entire task

Each reasoning step in an agentic loop requires loading context, retrieving tools, and writing intermediate outputs — all memory bandwidth operations. SK Hynix management explicitly called out in their Q4 2025 call that "demand continues to exceed supply even as output is maximized."

### Supply-Demand Reality Check

**Demand side:**
- AI hyperscalers (Microsoft/OpenAI Stargate, Google, Meta, Amazon) are in an infrastructure arms race
- Stargate alone has committed to 900,000 HBM wafers through SK Hynix
- Server DRAM prices up 60–70% from prior cycle lows
- TrendForce: DRAM contract prices rising across all segments through Q1 2026
- S&P Global: Samsung's revenue per bit from conventional DRAM forecast to rise **116% YoY in 2026**

**Supply side:**
- Samsung and SK Hynix control ~90% of HBM capacity
- New fab construction: 2–3 year lead time minimum
- Existing capacity allocated to HBM means legacy DRAM supply is tightening — conventional server DDR5 also rising
- SK Hynix: Q4 2025 operating margin of **58%** — pricing power is real

### Who Wins?

**SK Hynix** is the pure-play winner. 44% profit margins. 66% revenue growth. HBM3E market leadership. Target price of ₩1,332,730 vs. current ₩876,000 — **52% upside alone** from current levels, per analyst consensus.

**Samsung** is more complex — semiconductor division is booming, but mobile, TVs, and displays face consumer cycles. Still, memory business (37.1T KRW in Q4 alone, +62% YoY) is now large enough to drive the whole company.

---

## Step 3 — Valuation Model

### EWY Relative Valuation

| Scenario | EWY Price | Upside/Downside | Probability |
|----------|-----------|-----------------|-------------|
| Bear Case | $100–108 | -12% to -19% | 20% |
| Base Case | $145–155 | +18% to +26% | 55% |
| Bull Case | $165–175 | +34% to +42% | 25% |

**Expected Value:** (0.20 × $104) + (0.55 × $150) + (0.25 × $170) = **$144.10** (+17% from $122.87)

### Implied EWY Multiples

| Scenario | EWY P/E | Commentary |
|----------|---------|------------|
| Current | 16.5x | Peak-cycle discount applied |
| Bear | 13–14x | Cycle peaks, multiples compress |
| Base | 18–20x | HBM supercycle proves durable, re-rating |
| Bull | 22–25x | Structural memory shortage confirmed |

### Samsung + SK Hynix Individual Targets

**SK Hynix:** Based on analyst mean target ₩1,332,730 vs. ₩876,000 current:
- If Samsung + SK Hynix together are 41% of EWY...
- And SK Hynix alone has 52% upside to target...
- And Samsung has 29% upside to target...
- Combined contribution to EWY upside: ~41% × avg(52%, 29%) = ~33% of EWY's upside comes from just these two names

The remaining 59% of EWY provides optionality on Hyundai, KB Financial, Naver, and other Korean industrials.

---

## Step 4 — Risk Assessment

### Risk 1: Oil Price Sensitivity — MEDIUM (Managed)

South Korea imports **70% of its oil needs**. High oil ($112 currently) is a KRW headwind — it weakens the won, which raises input costs for Korean industry broadly. 

**However — this is nuanced for our thesis.** Samsung and SK Hynix are exporters paid in USD. A weaker KRW **inflates** their reported earnings when translated back. The ~70% oil import dependency mostly hurts Hyundai, refiners, and domestic industrials — not the chip exporters who dominate EWY's weighting.

The risk materializes if oil spikes to $130+ and triggers Korean current account stress. At $112–120, the net effect on the chip exporters is likely slightly positive via FX.

### Risk 2: Cyclical Peak — HIGH (Legitimate)

Memory is historically cyclical. The risk is real: what if we're at a cycle peak right now? SK Hynix at 58% operating margins is historically extreme. 

**Counterpoint:** This cycle may be different. Previous memory cycles were driven by PC and mobile demand. This one is driven by AI infrastructure — a secular buyer with multi-year procurement commitments. Microsoft, Google, Meta, and Amazon are not speculative. They are building AI datacenters with 3–5 year infrastructure roadmaps. The Stargate 900,000 wafer commitment is not a one-quarter demand spike.

The difference: AI hyperscalers are signing **long-term supply contracts** to hoard HBM. They learned from the 2023–2024 shortage. This time they're locking in supply ahead of demand. That changes the cycle dynamics.

### Risk 3: China Geopolitical Risk — MEDIUM

US export controls on advanced chips to China are ongoing. Samsung and SK Hynix both have exposure to the Chinese market. A further escalation could disrupt operations or force difficult geographic rebalancing.

**Mitigant:** Both companies are actively diversifying capacity to Korea (M15X expansion, Yongin) and the US (Samsung Taylor fab, SK Hynix Indiana packaging facility). The structural trend toward AI-memory independence from China is a long-term positive for Korean semiconductor margins.

### Risk 4: Korean Won Weakness — MEDIUM

USD/KRW at 1,510 is elevated. A sharp reversal (USD weakening) would reduce translated earnings for these Korean exporters. This is a real risk but cuts both ways — it also means current levels reflect a worst-case FX scenario to some degree.

### Risk 5: Concentration — LOW-MEDIUM

Samsung + SK Hynix at 41% of the fund is highly concentrated in two names. If either has a manufacturing disaster (yield problem, fire, earthquake), the thesis takes a direct hit. SK Hynix had a major fire in 2013 that destroyed supply — not unimaginable.

### Risk 6: Overly Optimistic Agentic AI Timeline — MEDIUM

Sansar's 10–15x compute multiplier for agentic AI is an approximation. If agentic AI development stalls, or if efficiency improvements offset the compute increase (smaller, more efficient models), demand may not materialize as expected. The thesis depends on the thesis that **reasoning steps = memory bandwidth consumption**. If models become more efficient at context management, this assumption weakens.

**Mitigant:** SK Hynix's Q4 2025 results already show demand exceeding supply at current AI scale — before agentic AI even reaches mass deployment. The base load from current AI infrastructure is already enough to drive the cycle. Agentic AI becomes the upside catalyst, not the core case.

---

## Step 5 — Investment Decision

### Base Case (55% probability): EWY reaches $145–155 in 12 months

HBM4 ramps successfully in 2026. AI infrastructure spending continues. DRAM pricing remains elevated. SK Hynix posts another year of record earnings. Samsung's memory division drives overall profit expansion. EWY re-rates from 16.5x to 18–20x earnings as the market accepts this is a structural shift, not a cycle peak.

### Bull Case (25%): EWY reaches $165–175

Agentic AI goes mainstream faster than expected. Memory wall problem intensifies as AI reasoning models scale. Supply constraints prove even tighter than expected. SK Hynix and Samsung both hit price targets well ahead of schedule. EWY re-rates to 22–25x.

### Bear Case (20%): EWY falls to $100–108

The memory cycle peaks earlier than expected. AI infrastructure spending slows (recession, rate shock, or correction in hyperscaler capex). The geopolitical risk from high oil or Korean won weakness triggers broader market rotation out of EWY. 

---

## Conclusion

The market is applying a cycle-peak discount to two companies reporting the strongest fundamental results in their corporate histories. SK Hynix posted 90% earnings growth and 58% operating margins. Samsung posted 155% earnings growth. Server DRAM prices are up 60–70%. HBM is in structural shortage.

EWY at $122.87, 20% below its 52-week high, is pricing maximum pessimism about the memory cycle's durability. But the buyers signing long-term HBM supply contracts are not speculative. Microsoft, Google, Meta, and Amazon don't panic-buy 900,000 wafers on a whim.

The 41% combined weight in Samsung and SK Hynix is not a bug — it is the thesis. A rising tide lifts these two, and they lift EWY with them.

**SPECULATIVE BUY. 12-month horizon. Size accordingly.**

---

## Monday Lesson (for Sansar)

*What did I learn from building this thesis?*

The most important thing I learned: **the agentic AI compute demand story is real, but it's not the only story**. The base load of AI infrastructure spending — current LLMs, current training runs, current inference — is already enough to drive a multi-year memory supercycle. Agentic AI is the catalyst that extends the cycle, not the catalyst that starts it.

The harder question: **at what price is the cycle priced in?** At 16.5x earnings with 40%+ earnings growth, EWY looks cheap. At 25x earnings at cycle peak, it's expensive. Timing matters. The pullback to $122 from $154 is the market expressing uncertainty about cycle length — uncertainty that I believe is overdone.

---

*Standard disclaimer: This thesis is for educational and research purposes only. It is not financial advice. Sansar is 14 years old and not a licensed investment advisor. Always do your own research and consult a financial advisor before making investment decisions.*

---

**Document version:** 1.0
**Built:** April 4, 2026
**Thesis type:** ETF Single-Country (South Korea)
**Coverage:** EWY, Samsung Electronics (005930.KS), SK Hynix (000660.KS)
**Tools used:** yfinance, web search (Futurum Research, TrendForce, ChosunBiz, S&P Global, StockAnalysis, GuruFocus)
