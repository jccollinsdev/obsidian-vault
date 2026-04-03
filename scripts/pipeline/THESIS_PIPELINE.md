# THESIS PIPELINE — /thesis Workflow

**Date Created:** April 3, 2026
**Purpose:** Formal process for building institutional-grade equity research theses

---

## Overview

Every `/thesis [idea]` run follows this exact sequence:

1. Pull live data
2. Run Quality of Earnings check
3. Build DCF model
4. Build NAV model (for miners/resource companies)
5. Build Trading Comps
6. Run Consistency Check ← **MANDATORY**
7. Scenario Analysis + Risk Matrix
8. Price Target + Recommendation
9. Finalize + Deliver

**The consistency check is non-negotiable.** If it fails, fix the model before presenting anything to Sansar.

---

## Calibration (from Sansar, Apr 3, 2026)

> Be conservative and harsh. Not every idea will work. Model correctly first — don't let assumptions drift to make the thesis look better. If the model says "this doesn't work," say so clearly.

---

## Step-by-Step Process

### Step 1 — Data Pull

Pull the following real data from live sources:
- Income statement: revenue, EBITDA, EBIT, net income (last 4 quarters + 3 years annual)
- Balance sheet: total debt, cash, net debt, shares outstanding, book value
- Cash flow statement: operating cash flow, capex, free cash flow
- For miners specifically: AISC, production volume (oz/year), proven reserves, mine life, reserve replacement ratio
- Market data: current price, market cap, EV, 52-week range
- Peer group: pull same metrics for 4-5 comparable companies

**Tool:** yfinance. Always use live data. Never simulate.

---

### Step 2 — Quality of Earnings Check

Before building any model, run the QoE check:

- FCF conversion ratio (FCF / net income) — flag if below 80%
- Accruals ratio — flag if rising
- Revenue recognition red flags — compare DSO trend
- Debt-adjusted return on equity trend

**If QoE fails, flag it explicitly. A thesis built on bad earnings quality is not a thesis worth making.**

---

### Step 3 — DCF Model

Using the data pulled:
- Project revenue for 5 years using conservative/base/bull growth assumptions
- Derive EBITDA margins from historical average and trend
- Calculate unlevered free cash flow each year:
  `UFCF = EBIT(1-tax rate) + D&A - capex - change in working capital`
- Calculate WACC:
  - Cost of equity via CAPM (use 10yr treasury as risk-free rate, pull current beta, use 5% equity risk premium)
  - Cost of debt = interest expense / total debt
  - Weight by market cap vs debt
- Terminal value using both:
  - Exit multiple method (EV/EBITDA × year 5 EBITDA)
  - Gordon Growth Model (FCF × (1+g) / (WACC-g), use g=2.5%)
- Discount all cash flows + terminal value back to present
- Subtract net debt, divide by shares outstanding
- Show implied share price

---

### Step 4 — NAV Model (for miners/resource companies)

- For each major asset/mine:
  - Annual production × (commodity price - AISC) = annual FCF
  - Discount over mine life at asset-level discount rate
  - Sum = NAV of that asset
- Sum all asset NAVs
- Add: cash, investments, undrilled exploration value
- Subtract: corporate debt, reclamation liabilities, G&A PV
- Divide by shares outstanding = NAV per share
- Run at bear/base/bull commodity price assumptions
- Calculate P/NAV at current price vs peer P/NAV multiples

---

### Step 5 — Trading Comps (EV/EBITDA, P/E, EV/FCF)

For the company and each peer:
- Calculate: EV/EBITDA (NTM), P/E (NTM), EV/FCF, P/NAV, FCF yield
- Build a comps table
- Identify where the company trades at premium/discount vs peers
- Implied price at peer median multiples for each metric

---

### Step 6 — Consistency Check (MANDATORY)

After building all models, run consistency verification:

**Check 1: DCF vs NAV directional agreement**
- At the same commodity price assumption, do both DCF and NAV produce values that increase in the same direction?
- If DCF says $100 and NAV says $80 at $4,000 gold, but DCF says $150 and NAV says $120 at $5,000 gold — that's fine (both go up with gold)
- If DCF goes up but NAV goes down at the same gold price — that's a contradiction that must be resolved

**Check 2: Scenario targets derived from models**
- Scenario price targets must be mathematically derived from DCF/NAV outputs, not hardcoded
- If scenario targets don't match the model outputs, flag and reconcile

**Check 3: BUY threshold**
- BUY recommendation requires >10% upside from current price to base case target
- If upside is <10%, either downgrade to HOLD or re-examine assumptions

**Check 4: Bear < Base < Bull**
- Verify bear case < base case < bull case for all price targets
- Any inversion is a modeling error

**Check 5: Risk matrix arithmetic**
- Sum of probability-weighted risks should reconcile to risk-adjusted target
- Risk-adjusted target should be between base and bear in most cases

**If any check fails:**
1. Identify the root cause
2. Fix the model (not the output)
3. Re-run consistency check
4. Only proceed when all checks pass

---

### Step 7 — Scenario Analysis

Define three scenarios with specific, justified assumptions:
- **Bear:** [specific macro + company-level assumptions]
- **Base:** [specific macro + company-level assumptions]
- **Bull:** [specific macro + company-level assumptions]

For each scenario run the full DCF and NAV.
Output: implied price, upside/downside from current, key assumption that differentiates each scenario.

---

### Step 8 — Risk Matrix

For each material risk:
- Describe the risk
- Quantify the impact on your base case price target
- Assign probability
- Calculate probability-weighted impact

Sum all risks into an adjusted price target.

---

### Step 9 — Price Target and Recommendation

- Weight your valuation methods: [e.g. 50% DCF, 30% NAV, 20% comps]
- Calculate blended price target
- State upside/downside to current price
- State recommendation: Buy / Hold / Sell
- State the ONE key variable that determines if you're right or wrong

**BUY threshold:** >10% upside to risk-adjusted target from current price.

---

## Output Format

Every thesis deliverable includes:
1. Consistency check results (before the thesis body)
2. All math shown explicitly — no black box conclusions
3. Every assumption sourced or justified
4. Flags for estimated vs. pulled-from-filings data
5. One-page executive summary at the top
6. Honest assessment of the entry point (is it cheap or fair?)

---

## Thesis That Don't Work

If the consistency check reveals the thesis doesn't hold up:
- Tell Sansar clearly: "This idea doesn't work because..."
- Show him the specific model outputs that contradict the thesis
- Suggest what would need to be true for the thesis to work
- Do not present a thesis that survives only because assumptions were tweaked

**A thesis that doesn't work is still valuable information. A thesis that sounds good but is wrong costs money.**

---

*This document is locked in as of April 3, 2026.*
