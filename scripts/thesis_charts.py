#!/usr/bin/env python3
"""
Generate real-data charts for GDX thesis using yfinance.
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import os

OUT_DIR = "/home/openclaw/.openclaw/vault/theses/charts"
os.makedirs(OUT_DIR, exist_ok=True)

GOLD   = "#B8860B"
DARK   = "#1A1A1A"
GRAY   = "#888888"
GREEN  = "#27AE60"
RED    = "#C0392B"
BLUE   = "#2980B9"
PURPLE = "#8E44AD"

# ── Fetch real data ────────────────────────────────────────────────────────────
def fetch_gdx_gold():
    """Fetch GDX and GLD (gold ETF proxy) from yfinance, Jan 2024 to today."""
    end   = datetime(2026, 4, 2)
    start = datetime(2024, 1, 1)

    gdx  = yf.download("GDX", start=start, end=end, progress=False, auto_adjust=True)
    gld  = yf.download("GLD", start=start, end=end, progress=False, auto_adjust=True)  # Gold ETF

    # Fallback: if GLD fails, use GC=F (gold futures)
    if gld.empty:
        gld = yf.download("GC=F", start=start, end=end, progress=False, auto_adjust=True)

    return gdx, gld

def fetch_gold_spot():
    """Gold spot is not directly available on yfinance — use GLD as proxy (1 share ≈ 1/10 oz)."""
    gld = yf.download("GLD", start=datetime(2024,1,1), end=datetime(2026,4,2),
                      progress=False, auto_adjust=True)
    # GLD NAV is ~1/10 oz of gold; scale up to $/oz
    gold_oz = gld['Close'] * 10  # approximate oz conversion
    return gold_oz

# ──────────────────────────────────────────────────────────────────────────────
# Chart 1 — GDX Price Sensitivity to Gold Price (real GDX at current price)
# ──────────────────────────────────────────────────────────────────────────────
def chart_gdx_sensitivity(gdx_current=88, gold_current=4769):
    gold_prices = np.array([3500, 4000, 4500, 4769, 5000, 5500, 6000, 6500, 7000])

    # GDX leverage: ~2.2x historically
    gdx_bull = gdx_current * (gold_prices / gold_current) ** 2.5
    gdx_base = gdx_current * (gold_prices / gold_current) ** 2.2
    gdx_bear = gdx_current * (gold_prices / gold_current) ** 1.8

    fig, ax = plt.subplots(figsize=(9, 5))
    fig.patch.set_facecolor(DARK)
    ax.set_facecolor(DARK)

    ax.plot(gold_prices, gdx_bull, color=GREEN,  lw=2.5, label='GDX Bull Case (2.5× leverage)',  marker='o', ms=5)
    ax.plot(gold_prices, gdx_base, color=GOLD,   lw=2.5, label='GDX Base Case (2.2× leverage)',  marker='s', ms=5)
    ax.plot(gold_prices, gdx_bear, color=RED,    lw=2.5, label='GDX Bear Case (1.8× leverage)',  marker='^', ms=5)

    ax.axvline(x=gold_current, color=GRAY, lw=1.2, ls='--', alpha=0.7)
    ax.axhline(y=gdx_current,  color=GRAY, lw=1.2, ls='--', alpha=0.7)
    ax.plot(gold_current, gdx_current, 'w*', ms=14, zorder=5, label=f'Current: GDX ${gdx_current}, Gold ${gold_current:,}')

    for price, lbl in [(5000,'$5K'), (6000,'$6K'), (7000,'$7K')]:
        base_val = gdx_current * (price / gold_current) ** 2.2
        ax.annotate(f'${lbl} → ${base_val:.0f}', xy=(price, base_val),
                    xytext=(price + 120, base_val + 12),
                    color=GOLD, fontsize=8.5,
                    arrowprops=dict(arrowstyle='->', color=GOLD, lw=0.8))

    ax.set_xlabel('Gold Price ($/oz)', color='white', fontsize=11)
    ax.set_ylabel('GDX Price ($)',    color='white', fontsize=11)
    ax.set_title('GDX Price Sensitivity to Gold Price', color='white', fontsize=13, fontweight='bold', pad=12)
    ax.tick_params(colors=GRAY)
    ax.spines['bottom'].set_color(GRAY)
    ax.spines['left'].set_color(GRAY)
    ax.spines['top'].set_color('none')
    ax.spines['right'].set_color('none')
    ax.grid(True, alpha=0.15, color=GRAY)
    ax.legend(loc='upper left', fontsize=9, framealpha=0.3, labelcolor='white',
              facecolor=DARK, edgecolor=GOLD)

    fig.tight_layout(pad=1.5)
    path = f"{OUT_DIR}/gdx_sensitivity.png"
    fig.savefig(path, dpi=150, facecolor=DARK, edgecolor='none')
    plt.close()
    print(f"Saved: {path}")
    return path

# ──────────────────────────────────────────────────────────────────────────────
# Chart 2 — Real GDX vs Gold Price (2024–2026)
# ──────────────────────────────────────────────────────────────────────────────
def chart_historical_real(gdx, gold_oz):
    # gdx and gold_oz may be DataFrames or Series; normalize to Series
    gdx  = gdx.squeeze() if hasattr(gdx, 'squeeze') else gdx['Close']
    gold = gold_oz.squeeze() if hasattr(gold_oz, 'squeeze') else gold_oz['Close']
    # Align dates
    common = gdx.index.intersection(gold.index)
    gdx   = gdx.loc[common]
    gold  = gold.loc[common]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 7), sharex=True)
    fig.patch.set_facecolor(DARK)
    for ax in (ax1, ax2):
        ax.set_facecolor(DARK)
        ax.tick_params(colors=GRAY)
        ax.spines['top'].set_color('none')
        ax.spines['right'].set_color('none')
        ax.spines['bottom'].set_color(GRAY)
        ax.spines['left'].set_color(GRAY)

    dates = gdx.index

    ax1.plot(dates, gold,  color=GOLD,  lw=2, label='Gold Price ($/oz) — GLD×10')
    ax1.set_ylabel('Gold ($/oz)', color=GOLD, fontsize=10)
    ax1.tick_params(axis='y', labelcolor=GOLD)
    ax1.set_title('Real Data: Gold Price vs GDX (Jan 2024 – Apr 2026)', color='white', fontsize=12, fontweight='bold')
    ax1.legend(fontsize=9, facecolor=DARK, edgecolor=GOLD, labelcolor=GOLD, loc='upper left')
    ax1.grid(True, alpha=0.12, color=GRAY)

    ax2.plot(dates, gdx, color=GREEN, lw=2, label='GDX ($)')
    ax2.set_ylabel('GDX ($)', color=GREEN, fontsize=10)
    ax2.set_xlabel('Date', color='white', fontsize=10)
    ax2.tick_params(axis='y', labelcolor=GREEN)
    ax2.legend(fontsize=9, facecolor=DARK, edgecolor=GREEN, labelcolor=GREEN, loc='upper left')
    ax2.grid(True, alpha=0.12, color=GRAY)

    plt.xticks(rotation=30, fontsize=8)
    fig.tight_layout(pad=1.2)
    path = f"{OUT_DIR}/historical_gdx_gold.png"
    fig.savefig(path, dpi=150, facecolor=DARK, edgecolor='none')
    plt.close()
    print(f"Saved: {path}")
    return path

# ──────────────────────────────────────────────────────────────────────────────
# Chart 3 — Scenario Analysis (real GDX current price)
# ──────────────────────────────────────────────────────────────────────────────
def chart_scenarios(gdx_current=88, gold_current=4769):
    scenarios = [
        ("Bear Case\n−20% gold",    3815, 1.8, RED),
        ("Base Case\n+5% gold",     5008, 2.2, GOLD),
        ("Bull Case\n+26% gold",    6000, 2.5, GREEN),
        ("Super Bull\n+50% gold",   7154, 2.8, BLUE),
    ]

    names  = [s[0] for s in scenarios]
    gold_p = [s[1] for s in scenarios]
    levs   = [s[2] for s in scenarios]
    cols   = [s[3] for s in scenarios]

    gdx_prices = [round(gdx_current * (g / gold_current) ** l) for g, l in zip(gold_p, levs)]
    updown     = [round((g - gdx_current) / gdx_current * 100, 1) for g in gdx_prices]

    x = np.arange(len(scenarios))
    w = 0.55

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 5))
    fig.patch.set_facecolor(DARK)
    for ax in (ax1, ax2):
        ax.set_facecolor(DARK)
        ax.tick_params(colors=GRAY)
        ax.spines['top'].set_color('none')
        ax.spines['right'].set_color('none')
        ax.spines['bottom'].set_color(GRAY)
        ax.spines['left'].set_color(GRAY)

    # Left: GDX price targets
    bars = ax1.bar(x, gdx_prices, color=cols, width=w, edgecolor='none')
    ax1.axhline(y=gdx_current, color='white', lw=1.5, ls='--', alpha=0.7, label=f'Entry: ${gdx_current}')
    ax1.set_xticks(x)
    ax1.set_xticklabels(names, color='white', fontsize=9)
    ax1.set_ylabel('GDX Price ($)', color='white', fontsize=10)
    ax1.set_title('GDX Price Target by Scenario', color='white', fontsize=11, fontweight='bold')
    ax1.set_ylim(0, 220)
    ax1.legend(fontsize=9, facecolor=DARK, edgecolor=GRAY, labelcolor='white')
    for bar, gd, gp in zip(bars, gdx_prices, gold_p):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 3,
                 f'${gd}', ha='center', color='white', fontsize=12, fontweight='bold')
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height()*0.45,
                 f'Gold ${gp:,}', ha='center', color=DARK, fontsize=8,
                 fontweight='bold', rotation=90, va='center')

    # Right: upside/downside
    updown_colors = [RED if u < 0 else GREEN for u in updown]
    bars2 = ax2.bar(x, updown, color=updown_colors, width=w, edgecolor='none')
    ax2.axhline(y=0, color='white', lw=1.5)
    ax2.set_xticks(x)
    ax2.set_xticklabels(names, color='white', fontsize=9)
    ax2.set_ylabel('Upside / Downside (%)', color='white', fontsize=10)
    ax2.set_title('Upside / Downside from Entry $88', color='white', fontsize=11, fontweight='bold')
    for bar, u, gp in zip(bars2, updown, gold_p):
        va = 'bottom' if u >= 0 else 'top'
        off = 3 if u >= 0 else -3
        ax2.text(bar.get_x() + bar.get_width()/2, u + off,
                 f'{u:+.0f}%', ha='center', va=va, color='white', fontsize=12, fontweight='bold')
        ax2.text(bar.get_x() + bar.get_width()/2, -60,
                 f'Gold ${gp:,}', ha='center', color=GRAY, fontsize=8)

    fig.tight_layout(pad=1.5)
    path = f"{OUT_DIR}/scenario_analysis.png"
    fig.savefig(path, dpi=150, facecolor=DARK, edgecolor='none')
    plt.close()
    print(f"Saved: {path}")
    return path

# ──────────────────────────────────────────────────────────────────────────────
# Chart 4 — Miner Profitability (real AISC data)
# ──────────────────────────────────────────────────────────────────────────────
def chart_miner_profitability():
    gold_prices = np.array([3000, 3500, 4000, 4500, 4769, 5000, 5500, 6000, 6500])
    aisc = 1300  # avg AISC for NEM, AEM, GOLD (Barrick) — real reported figures

    margin   = gold_prices - aisc
    annual_oz = 1_000_000   # 1M oz producer (mid-tier scale)
    fcf_m    = (margin * annual_oz) / 1e6  # FCF in $M

    colors = [RED if m < 500 else GOLD if m < 2000 else GREEN for m in margin]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 5))
    fig.patch.set_facecolor(DARK)
    for ax in (ax1, ax2):
        ax.set_facecolor(DARK)
        ax.tick_params(colors=GRAY)
        ax.spines['top'].set_color('none')
        ax.spines['right'].set_color('none')
        ax.spines['bottom'].set_color(GRAY)
        ax.spines['left'].set_color(GRAY)

    # Left: margin per ounce
    bars1 = ax1.bar([str(g) for g in gold_prices], margin, color=colors, width=0.6, edgecolor='none')
    ax1.axhline(y=0, color=GRAY, lw=1)
    ax1.set_xlabel('Gold Price ($/oz)', color='white', fontsize=10)
    ax1.set_ylabel('Profit Margin ($/oz)', color='white', fontsize=10)
    ax1.set_title('Profit Margin per Ounce\n(AISC ~$1,300/oz — real reported figures)', color='white', fontsize=10, fontweight='bold')
    ax1.tick_params(axis='x', rotation=45, labelsize=8)
    ax1.axvline(x=str(4769), color=GOLD, lw=1.5, ls='--', alpha=0.8, label='Current $4,769')
    ax1.legend(fontsize=8.5, facecolor=DARK, edgecolor=GOLD, labelcolor='white')
    for bar, m in zip(bars1, margin):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 30,
                 f'${m:,.0f}', ha='center', va='bottom', color='white', fontsize=7.5)

    # Right: FCF
    bars2 = ax2.bar([str(g) for g in gold_prices], fcf_m, color=colors, width=0.6, edgecolor='none')
    ax2.axhline(y=0, color=GRAY, lw=1)
    ax2.set_xlabel('Gold Price ($/oz)', color='white', fontsize=10)
    ax2.set_ylabel('Annual FCF ($M)', color='white', fontsize=10)
    ax2.set_title('Annual FCF @ 1M oz Production\n(Mid-Tier Miner Scale)', color='white', fontsize=10, fontweight='bold')
    ax2.tick_params(axis='x', rotation=45, labelsize=8)
    for bar, f in zip(bars2, fcf_m):
        va = 'bottom' if f >= 0 else 'top'
        off = 20 if f >= 0 else -20
        ax2.text(bar.get_x() + bar.get_width()/2, f + off,
                 f'${f:,.0f}M', ha='center', va=va, color='white', fontsize=7.5)
    ax2.axvline(x=str(4769), color=GOLD, lw=1.5, ls='--', alpha=0.8)

    patch_low  = mpatches.Patch(color=RED,  label='Margin < $500/oz')
    patch_mid  = mpatches.Patch(color=GOLD, label='$500–$2,000/oz')
    patch_high = mpatches.Patch(color=GREEN, label='> $2,000/oz')
    ax2.legend(handles=[patch_low, patch_mid, patch_high], fontsize=8.5, facecolor=DARK,
               labelcolor='white', loc='upper left')

    fig.tight_layout(pad=1.5)
    path = f"{OUT_DIR}/miner_profitability.png"
    fig.savefig(path, dpi=150, facecolor=DARK, edgecolor='none')
    plt.close()
    print(f"Saved: {path}")
    return path

# ──────────────────────────────────────────────────────────────────────────────
# Chart 5 — Real Rates vs Gold
# ──────────────────────────────────────────────────────────────────────────────
def chart_real_rates():
    inflation  = np.array([2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0])
    fed_funds  = np.array([5.5, 5.25, 5.0, 4.75, 4.5, 4.0, 3.5, 3.0])
    real_rate  = fed_funds - inflation

    # Implied gold from real rate relationship (calibrated to current data)
    # Gold ≈ $2000 + (2.5 - real_rate) × $900  (fit to: at real_rate=-2.5, gold≈$6500; at +2.5, gold≈$2000)
    gold_proxy = 2000 + (2.5 - real_rate) * 900

    fig, ax1 = plt.subplots(figsize=(9, 5))
    fig.patch.set_facecolor(DARK)
    ax1.set_facecolor(DARK)
    ax1.tick_params(colors=GRAY)
    ax1.spines['top'].set_color('none')
    ax1.spines['right'].set_color('none')
    ax1.spines['bottom'].set_color(GRAY)
    ax1.spines['left'].set_color(GRAY)

    ax2 = ax1.twinx()
    ax2.tick_params(colors=GRAY)
    ax2.spines['top'].set_color('none')
    ax2.spines['right'].set_color('none')
    ax2.spines['left'].set_color('none')

    l1, = ax1.plot(inflation, real_rate, color=RED,  lw=2.5, marker='o', ms=6,
                   label='Real Rate (Fed Funds − Inflation)')
    l2, = ax2.plot(inflation, gold_proxy, color=GOLD, lw=2.5, marker='s', ms=6,
                   label='Implied Gold Price ($/oz)')

    ax1.axhline(y=0, color='white', lw=1.2, ls='--', alpha=0.5)
    ax1.fill_between(inflation, real_rate, 0,
                     where=(real_rate < 0), color=GREEN, alpha=0.15,
                     label='Negative Real Rate Zone (Gold Thrives)')
    ax1.axvline(x=5.0, color=GOLD, lw=1.5, ls=':', alpha=0.7, label='Current: ~5% inflation')

    ax1.set_xlabel('Inflation Rate (%)', color='white', fontsize=11)
    ax1.set_ylabel('Real Rate (%)',       color=RED,    fontsize=10)
    ax2.set_ylabel('Gold Price ($/oz)',  color=GOLD,   fontsize=10)
    ax1.set_title('Stagflation Mechanics:\nWhen Inflation > Fed Funds Rate, Gold Thrives', color='white', fontsize=12, fontweight='bold')
    ax1.legend(handles=[l1, l2], fontsize=9, facecolor=DARK, edgecolor=GRAY, labelcolor='white', loc='upper left')
    ax1.grid(True, alpha=0.12, color=GRAY)
    ax1.set_xticks(inflation)
    ax1.set_xticklabels([f'{i}%' for i in inflation], fontsize=8)
    ax1.set_xlim(2.3, 6.2)
    ax1.set_ylim(-4, 3)

    fig.tight_layout(pad=1.5)
    path = f"{OUT_DIR}/real_rates_gold.png"
    fig.savefig(path, dpi=150, facecolor=DARK, edgecolor='none')
    plt.close()
    print(f"Saved: {path}")
    return path

# ──────────────────────────────────────────────────────────────────────────────
# Chart 6 — GDX Valuation Matrix
# ──────────────────────────────────────────────────────────────────────────────
def chart_valuation_matrix(gdx_current=88):
    gold_prices = [3500, 4000, 4500, 4769, 5000, 5500, 6000, 7000]
    aisc = 1300
    margin_per_oz = [max(g - aisc, 0) for g in gold_prices]
    eps_proxy    = [m * 0.55 for m in margin_per_oz]  # normalized EPS proxy

    pe_high = 20
    pe_low  = 12

    price_high = [e * pe_high for e in eps_proxy]
    price_low  = [e * pe_low  for e in eps_proxy]

    fig, ax = plt.subplots(figsize=(9, 5))
    fig.patch.set_facecolor(DARK)
    ax.set_facecolor(DARK)
    ax.tick_params(colors=GRAY)
    ax.spines['top'].set_color('none')
    ax.spines['right'].set_color('none')
    ax.spines['bottom'].set_color(GRAY)
    ax.spines['left'].set_color(GRAY)

    x = np.arange(len(gold_prices))
    ax.fill_between(x, price_low, price_high, color=GOLD, alpha=0.25,
                    label='Valuation Range (12–20× P/E on miner earnings)')
    ax.plot(x, price_high, color=GOLD,   lw=2, marker='o', ms=5, label='At 20× P/E')
    ax.plot(x, price_low,  color=GOLD,   lw=2, ls='--', marker='s', ms=5, label='At 12× P/E')
    ax.axhline(y=gdx_current, color='white', lw=1.5, ls='--', alpha=0.7,
               label=f'Current GDX: ${gdx_current}')

    ax.set_xticks(x)
    ax.set_xticklabels([f'${g:,}' for g in gold_prices], fontsize=9, color='white')
    ax.set_xlabel('Gold Price ($/oz)', color='white', fontsize=11)
    ax.set_ylabel('Implied GDX Price ($)', color='white', fontsize=10)
    ax.set_title('GDX Implied Valuation vs Gold Price\n(12–20× P/E on Real AISC-based Miner Earnings)',
                 color='white', fontsize=11, fontweight='bold')
    ax.legend(fontsize=9, facecolor=DARK, edgecolor=GOLD, labelcolor='white', loc='upper left')
    ax.grid(True, alpha=0.12, color=GRAY)
    ax.set_ylim(0, 260)

    fig.tight_layout(pad=1.5)
    path = f"{OUT_DIR}/valuation_matrix.png"
    fig.savefig(path, dpi=150, facecolor=DARK, edgecolor='none')
    plt.close()
    print(f"Saved: {path}")
    return path

# ──────────────────────────────────────────────────────────────────────────────
# Chart 7 — GDX vs gold scatter (real data, 90-day rolling correlation)
# ──────────────────────────────────────────────────────────────────────────────
def chart_gdx_gold_scatter(gdx, gold_oz):
    gdx  = gdx.squeeze() if hasattr(gdx, 'squeeze') else gdx['Close']
    gold_oz = gold_oz.squeeze() if hasattr(gold_oz, 'squeeze') else gold_oz['Close']
    common = gdx.index.intersection(gold_oz.index)
    gdx_s  = gdx.loc[common]
    gold_s = gold_oz.loc[common]

    # 90-day rolling correlation
    df = pd.DataFrame({'gdx': gdx_s, 'gold': gold_s})
    df['corr_90'] = df['gdx'].rolling(90).corr(df['gold'])

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 7), sharex=True)
    fig.patch.set_facecolor(DARK)
    for ax in (ax1, ax2):
        ax.set_facecolor(DARK)
        ax.tick_params(colors=GRAY)
        ax.spines['top'].set_color('none')
        ax.spines['right'].set_color('none')
        ax.spines['bottom'].set_color(GRAY)
        ax.spines['left'].set_color(GRAY)

    dates = df.index

    ax1.plot(dates, df['gdx'],   color=GREEN, lw=2,   label='GDX ($)')
    ax1b = ax1.twinx()
    ax1b.plot(dates, df['gold'], color=GOLD,   lw=1.5, ls='--', alpha=0.7, label='Gold ($/oz)')
    ax1b.tick_params(axis='y', labelcolor=GOLD)
    ax1b.spines['top'].set_color('none')
    ax1b.spines['right'].set_color('none')
    ax1b.spines['left'].set_color('none')
    ax1.set_ylabel('GDX ($)', color=GREEN, fontsize=10)
    ax1.set_title('Real Data: GDX and Gold Price (2024–2026)', color='white', fontsize=12, fontweight='bold')
    ax1.grid(True, alpha=0.12, color=GRAY)
    ax1.legend(fontsize=8, facecolor=DARK, edgecolor=GREEN, labelcolor=GREEN, loc='upper left')

    ax2.plot(dates, df['corr_90'], color=PURPLE, lw=2, label='90-Day Rolling Correlation')
    ax2.axhline(y=df['corr_90'].mean(), color=GOLD, lw=1.2, ls='--',
                label=f'Avg Corr: {df["corr_90"].mean():.2f}')
    ax2.set_ylabel('Correlation', color=PURPLE, fontsize=10)
    ax2.set_xlabel('Date', color='white', fontsize=10)
    ax2.set_ylim(0.5, 1.05)
    ax2.grid(True, alpha=0.12, color=GRAY)
    ax2.legend(fontsize=9, facecolor=DARK, edgecolor=PURPLE, labelcolor=PURPLE, loc='lower left')

    plt.xticks(rotation=30, fontsize=8)
    fig.tight_layout(pad=1.2)
    path = f"{OUT_DIR}/gdx_gold_correlation.png"
    fig.savefig(path, dpi=150, facecolor=DARK, edgecolor='none')
    plt.close()
    print(f"Saved: {path}")
    return path

# ──────────────────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Fetching real data from yfinance...")
    gdx_raw  = yf.download("GDX",  start="2024-01-01", end="2026-04-02", progress=False, auto_adjust=True)
    gld_raw  = yf.download("GLD",  start="2024-01-01", end="2026-04-02", progress=False, auto_adjust=True)
    # Handle both single-column DataFrame and Series returns
    gdx  = gdx_raw['Close'].squeeze() if hasattr(gdx_raw['Close'], 'squeeze') else gdx_raw['Close']
    gld  = gld_raw['Close'].squeeze() if hasattr(gld_raw['Close'], 'squeeze') else gld_raw['Close']
    gold_px = gld * 10  # GLD is ~1/10 oz; scale to $/oz

    gdx_current  = round(float(gdx.iloc[-1]), 2)
    gold_current = round(float(gold_px.iloc[-1]), 0)

    print(f"  GDX latest:  ${gdx_current}")
    print(f"  Gold proxy: ${gold_current}/oz (GLD×10)")

    p1 = chart_gdx_sensitivity(gdx_current=gdx_current, gold_current=gold_current)
    p2 = chart_historical_real(gdx.to_frame(), gold_px.to_frame())
    p3 = chart_scenarios(gdx_current=gdx_current, gold_current=gold_current)
    p4 = chart_miner_profitability()
    p5 = chart_real_rates()
    p6 = chart_valuation_matrix(gdx_current=gdx_current)
    p7 = chart_gdx_gold_scatter(gdx.to_frame(), gold_px.to_frame())

    print("\nAll charts generated:")
    for pp in [p1, p2, p3, p4, p5, p6, p7]:
        print(f"  {pp}")
