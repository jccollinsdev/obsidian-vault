#!/usr/bin/env python3
"""
Generate the research PDF thesis for EWY — South Korea Memory ETF.
"""
import os
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, black, white
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, HRFlowable,
                                Table, TableStyle, KeepTogether, PageBreak)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT

OUTPUT_PATH = "/home/openclaw/.openclaw/vault/theses/EWY_Bullish_Korean_Memory.pdf"
CHARTS_DIR  = "/home/openclaw/.openclaw/vault/theses/charts"

GOLD    = HexColor("#1E4D8C"); GOLD_LIGHT = HexColor("#D6E4F0")
DARK_BG = HexColor("#1A1A1A"); LIGHT_BG   = HexColor("#FAFAFA")
TEXT    = HexColor("#1A1A1A"); GRAY       = HexColor("#777777")
GREEN   = HexColor("#27AE60"); RED        = HexColor("#C0392B")
BLUE    = HexColor("#1E4D8C"); ACCENT     = HexColor("#E74C3C")

EWY_CURRENT  = 122.87
EWY_HIGH     = 154.22
EWY_LOW      = 48.49

def section_bar(n, text):
    data = [[Paragraph(f"{n}  ·  {text.upper()}", ParagraphStyle(
        'SB', fontName='Helvetica-Bold', fontSize=11, textColor=white))]]
    t = Table(data, colWidths=[6.5*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND',    (0,0), (-1,-1), BLUE),
        ('TOPPADDING',    (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING',   (0,0), (-1,-1), 10),
    ]))
    return t

def meta_row():
    data = [[
        Paragraph("📊 THESIS", ParagraphStyle('m', fontName='Helvetica-Bold', fontSize=9, textColor=white, alignment=TA_CENTER)),
        Paragraph("EWY — iShares MSCI South Korea ETF", ParagraphStyle('m', fontName='Helvetica-Bold', fontSize=9, textColor=white, alignment=TA_CENTER)),
        Paragraph("SPECULATIVE BUY", ParagraphStyle('m', fontName='Helvetica-Bold', fontSize=9, textColor=GREEN, alignment=TA_CENTER)),
        Paragraph("12-MONTH HORIZON", ParagraphStyle('m', fontName='Helvetica-Bold', fontSize=9, textColor=white, alignment=TA_CENTER)),
    ]]
    t = Table(data, colWidths=[1.1*inch, 2.9*inch, 1.5*inch, 1.0*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND',    (0,0), (-1,-1), DARK_BG),
        ('TOPPADDING',    (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('ALIGN',         (0,0), (-1,-1), 'CENTER'),
        ('VALIGN',        (0,0), (-1,-1), 'MIDDLE'),
    ]))
    return t

def price_box():
    items = [
        ("Current Price", f"${EWY_CURRENT}"),
        ("52-Week High", f"${EWY_HIGH}"),
        ("52-Week Low", f"${EWY_LOW}"),
        ("Down from High", f"{((EWY_CURRENT-EWY_HIGH)/EWY_HIGH)*100:.1f}%"),
    ]
    data = [[Paragraph(k, ParagraphStyle('pk', fontName='Helvetica', fontSize=8, textColor=GRAY, alignment=TA_CENTER)),
             Paragraph(v, ParagraphStyle('pv', fontName='Helvetica-Bold', fontSize=11, textColor=DARK_BG, alignment=TA_CENTER))]
            for k, v in items]
    t = Table(data, colWidths=[1.625*inch]*4)
    t.setStyle(TableStyle([
        ('BOX',           (0,0), (-1,-1), 0.5, GOLD_LIGHT),
        ('INNERGRID',    (0,0), (-1,-1), 0.5, GOLD_LIGHT),
        ('BACKGROUND',    (0,0), (-1,-1), LIGHT_BG),
        ('TOPPADDING',   (0,0), (-1,-1), 5),
        ('BOTTOMPADDING',(0,0), (-1,-1), 5),
        ('ALIGN',         (0,0), (-1,-1), 'CENTER'),
    ]))
    return t

def target_box():
    scenarios = [
        ("Bear Case", "$100–$108", "-12% to -19%", RED),
        ("Base Case", "$145–$155", "+18% to +26%", GREEN),
        ("Bull Case", "$165–$175", "+34% to +42%", BLUE),
    ]
    data = [[
        Paragraph(f"<b>{label}</b>", ParagraphStyle('tl', fontName='Helvetica-Bold', fontSize=9, textColor=col, alignment=TA_CENTER)),
        Paragraph(price, ParagraphStyle('tp', fontName='Helvetica-Bold', fontSize=11, textColor=DARK_BG, alignment=TA_CENTER)),
        Paragraph(updown, ParagraphStyle('tu', fontName='Helvetica', fontSize=8, textColor=GRAY, alignment=TA_CENTER)),
    ] for label, price, updown, col in scenarios]
    t = Table(data, colWidths=[1.5*inch, 2.0*inch, 3.0*inch])
    t.setStyle(TableStyle([
        ('BOX',           (0,0), (-1,-1), 0.5, GOLD_LIGHT),
        ('INNERGRID',    (0,0), (-1,-1), 0.5, GOLD_LIGHT),
        ('BACKGROUND',    (0,0), (-1,-1), LIGHT_BG),
        ('TOPPADDING',   (0,0), (-1,-1), 6),
        ('BOTTOMPADDING',(0,0), (-1,-1), 6),
        ('ALIGN',         (0,0), (-1,-1), 'CENTER'),
    ]))
    return t

def h1(text):
    return Paragraph(text, ParagraphStyle('h1', fontName='Helvetica-Bold', fontSize=14,
                                           textColor=DARK_BG, spaceAfter=6, spaceBefore=12))

def h2(text):
    return Paragraph(text, ParagraphStyle('h2', fontName='Helvetica-Bold', fontSize=11,
                                           textColor=BLUE, spaceAfter=4, spaceBefore=8))

def body(text):
    return Paragraph(text, ParagraphStyle('body', fontName='Helvetica', fontSize=9,
                                            textColor=TEXT, leading=14, spaceAfter=4,
                                            alignment=TA_JUSTIFY))

def bold_body(text):
    return Paragraph(f"<b>{text}</b>", ParagraphStyle('bb', fontName='Helvetica-Bold', fontSize=9,
                                                        textColor=DARK_BG, leading=14, spaceAfter=4,
                                                        alignment=TA_JUSTIFY))

def bullet(text):
    return Paragraph(f"• {text}", ParagraphStyle('bul', fontName='Helvetica', fontSize=9,
                                                    textColor=TEXT, leading=14, spaceAfter=3,
                                                    leftIndent=12, alignment=TA_LEFT))

def spacer(h=0.1):
    return Spacer(1, h*inch)

def rule():
    return HRFlowable(width="100%", thickness=0.5, color=GOLD_LIGHT, spaceAfter=6)

doc = SimpleDocTemplate(
    OUTPUT_PATH,
    pagesize=letter,
    leftMargin=0.75*inch, rightMargin=0.75*inch,
    topMargin=0.75*inch, bottomMargin=0.75*inch,
)

styles = getSampleStyleSheet()
story = []

# ── Header ──────────────────────────────────────────────────────────────────
story.append(meta_row())
story.append(spacer(0.15))
story.append(price_box())
story.append(spacer(0.1))
story.append(target_box())
story.append(spacer(0.2))

# ── Executive Summary ───────────────────────────────────────────────────────
story.append(section_bar("EXECUTIVE SUMMARY", ""))
story.append(spacer(0.1))
story.append(body(
    "<b>Samsung Electronics (22.35%) and SK Hynix (18.78%) together comprise 41.1% of EWY.</b> "
    "These are not just holdings — they are the thesis. The market is underpricing how long and "
    "how deep the AI memory supercycle runs."
))
story.append(body(
    "Agentic AI doesn't just use more compute — it creates a structurally different memory demand "
    "profile. One prompt in an agentic system can trigger 10–15 sequential reasoning steps, each "
    "requiring memory bandwidth. The memory wall is not a bottleneck that gets solved — it is a "
    "permanent architectural constraint that gets worse as AI systems scale."
))
story.append(body(
    "Samsung and SK Hynix control approximately 90% of global HBM production. Supply cannot "
    "respond quickly. SK Hynix is running fabs at maximum utilization with 58% operating margins. "
    "Samsung just posted record memory revenue in Q4 2025 (+62% YoY). Server DRAM contract prices "
    "have risen 60–70% from prior cycle lows."
))
story.append(body(
    f"EWY sits at <b>${EWY_CURRENT}</b>, approximately 20% below its 52-week high of ${EWY_HIGH}. "
    "The market is applying a cycle-peak discount to companies reporting record earnings. That gap "
    "is the opportunity."
))
story.append(spacer(0.15))

# ── Consistency Checks ──────────────────────────────────────────────────────
story.append(section_bar("CONSISTENCY CHECKS", ""))
story.append(spacer(0.1))
checks = [
    ("1", "Agentic AI drives 10–15x more memory per task",
     "Defensible — agentic loops require persistent context and multi-step retrieval"),
    ("2", "HBM supply cannot respond fast enough",
     "Confirmed — Samsung and SK Hynix are capacity-constrained; new fabs take 2–3 years"),
    ("3", "Samsung + SK Hynix = 41% of EWY",
     "Confirmed — stockanalysis.com data: Samsung 22.35%, SK Hynix 18.78%"),
    ("4", "Oil price headwind is overstated for these companies",
     "Qualified — true for exporters, but oil → KRW weakness is a secondary risk"),
    ("5", "Forward PEs of 4–6x are artificially depressed",
     "Defensible — investors price a cyclical peak; if cycle extends, re-rating to 8–10x likely"),
    ("6", "EWY at $122 represents a pullback entry",
     "Confirmed — 20% below 52w high with fundamentals accelerating"),
]
check_data = [[
    Paragraph(f"<b>#{n}</b>", ParagraphStyle('cn', fontName='Helvetica-Bold', fontSize=8, textColor=BLUE)),
    Paragraph(title, ParagraphStyle('ct', fontName='Helvetica-Bold', fontSize=8, textColor=DARK_BG)),
    Paragraph(status, ParagraphStyle('cs', fontName='Helvetica', fontSize=8, textColor=GRAY)),
] for n, title, status in checks]
t = Table(check_data, colWidths=[0.35*inch, 2.8*inch, 3.35*inch])
t.setStyle(TableStyle([
    ('BOX',           (0,0), (-1,-1), 0.5, GOLD_LIGHT),
    ('INNERGRID',    (0,0), (-1,-1), 0.5, GOLD_LIGHT),
    ('BACKGROUND',    (0,0), (-1,-1), LIGHT_BG),
    ('TOPPADDING',   (0,0), (-1,-1), 4),
    ('BOTTOMPADDING',(0,0), (-1,-1), 4),
    ('LEFTPADDING',  (0,0), (-1,-1), 6),
    ('VALIGN',       (0,0), (-1,-1), 'TOP'),
]))
story.append(t)
story.append(Paragraph(
    "<b>Consistency Status: ALL CHECKS PASS — with noted risks</b>",
    ParagraphStyle('csFinal', fontName='Helvetica-Bold', fontSize=8, textColor=GREEN,
                   spaceBefore=4, alignment=TA_LEFT)
))
story.append(spacer(0.15))

# ── Key Holdings Data ────────────────────────────────────────────────────────
story.append(section_bar("KEY HOLDINGS DATA", ""))
story.append(spacer(0.1))

# SK Hynix
story.append(h2("SK Hynix (000660.KS) — 18.78% of EWY"))
sk_data = [
    ["Metric", "Value"],
    ["Price", "₩876,000"],
    ["52-Week High", "₩1,099,000"],
    ["52-Week Low", "₩162,700"],
    ["Down from High", "-20.3%"],
    ["Forward P/E", "~4.4x"],
    ["Revenue Growth (YoY)", "+66.1%"],
    ["Earnings Growth (QoQ)", "+90.2%"],
    ["Operating Margin", "58.4%"],
    ["Profit Margin", "44.2%"],
    ["Return on Equity", "44.1%"],
    ["Analyst Rating", "STRONG BUY (1.46/5)"],
    ["Target Mean Price", "₩1,332,730 (+52% upside)"],
]
t = Table(sk_data, colWidths=[2.2*inch, 4.3*inch])
t.setStyle(TableStyle([
    ('BACKGROUND',  (0,0), (-1,0), BLUE),
    ('TEXTCOLOR',   (0,0), (-1,0), white),
    ('FONTNAME',    (0,0), (-1,0), 'Helvetica-Bold'),
    ('FONTSIZE',    (0,0), (-1,-1), 8),
    ('BACKGROUND',  (0,1), (-1,-1), LIGHT_BG),
    ('ROWBACKGROUNDS', (0,1), (-1,-1), [LIGHT_BG, HexColor("#F0F4F8")]),
    ('BOX',         (0,0), (-1,-1), 0.5, GOLD_LIGHT),
    ('INNERGRID',   (0,0), (-1,-1), 0.3, GOLD_LIGHT),
    ('TOPPADDING', (0,0), (-1,-1), 3),
    ('BOTTOMPADDING',(0,0),(-1,-1), 3),
    ('LEFTPADDING', (0,0), (-1,-1), 6),
]))
story.append(t)
story.append(spacer(0.1))

# Samsung
story.append(h2("Samsung Electronics (005930.KS) — 22.35% of EWY"))
sam_data = [
    ["Metric", "Value"],
    ["Price", "₩186,200"],
    ["52-Week High", "₩223,000"],
    ["52-Week Low", "₩52,900"],
    ["Down from High", "-16.5%"],
    ["Forward P/E", "~6.5x"],
    ["Revenue Growth (YoY)", "+23.8%"],
    ["Earnings Growth (QoQ)", "+155.4%"],
    ["Operating Margin", "21.3%"],
    ["Profit Margin", "13.3%"],
    ["Return on Equity", "10.8%"],
    ["Target Mean Price", "₩239,873 (+29% upside)"],
]
t = Table(sam_data, colWidths=[2.2*inch, 4.3*inch])
t.setStyle(TableStyle([
    ('BACKGROUND',  (0,0), (-1,0), BLUE),
    ('TEXTCOLOR',   (0,0), (-1,0), white),
    ('FONTNAME',    (0,0), (-1,0), 'Helvetica-Bold'),
    ('FONTSIZE',    (0,0), (-1,-1), 8),
    ('ROWBACKGROUNDS', (0,1), (-1,-1), [LIGHT_BG, HexColor("#F0F4F8")]),
    ('BOX',         (0,0), (-1,-1), 0.5, GOLD_LIGHT),
    ('INNERGRID',   (0,0), (-1,-1), 0.3, GOLD_LIGHT),
    ('TOPPADDING', (0,0), (-1,-1), 3),
    ('BOTTOMPADDING',(0,0),(-1,-1), 3),
    ('LEFTPADDING', (0,0), (-1,-1), 6),
]))
story.append(t)
story.append(spacer(0.1))

# EWY top 5
story.append(h2("EWY Top 5 Holdings"))
holdings_data = [
    ["Rank", "Company", "Weight"],
    ["1", "Samsung Electronics", "22.35%"],
    ["2", "SK Hynix", "18.78%"],
    ["3", "Hyundai Motor", "2.66%"],
    ["4", "KB Financial Group", "2.32%"],
    ["5", "SK Square", "2.03%"],
]
t = Table(holdings_data, colWidths=[0.5*inch, 3.5*inch, 2.5*inch])
t.setStyle(TableStyle([
    ('BACKGROUND',  (0,0), (-1,0), DARK_BG),
    ('TEXTCOLOR',   (0,0), (-1,0), white),
    ('FONTNAME',    (0,0), (-1,0), 'Helvetica-Bold'),
    ('FONTSIZE',    (0,0), (-1,-1), 8),
    ('ROWBACKGROUNDS', (0,1), (-1,-1), [LIGHT_BG, HexColor("#F0F4F8")]),
    ('BOX',         (0,0), (-1,-1), 0.5, GOLD_LIGHT),
    ('INNERGRID',   (0,0), (-1,-1), 0.3, GOLD_LIGHT),
    ('TOPPADDING', (0,0), (-1,-1), 3),
    ('BOTTOMPADDING',(0,0),(-1,-1), 3),
    ('LEFTPADDING', (0,0), (-1,-1), 6),
    ('ALIGN',       (2,0), (2,-1), 'RIGHT'),
]))
story.append(t)
story.append(Paragraph(
    "<b>Samsung + SK Hynix = 41.13% of EWY.</b> Concentration risk — but also concentration opportunity.",
    ParagraphStyle('note', fontName='Helvetica', fontSize=8, textColor=GRAY, spaceBefore=4)
))
story.append(spacer(0.15))

# ── HBM Market Analysis ─────────────────────────────────────────────────────
story.append(section_bar("HBM MARKET ANALYSIS", ""))
story.append(spacer(0.1))
story.append(h2("The Memory Wall Is Getting Worse, Not Better"))
story.append(body(
    "The fundamental thesis rests on a structural imbalance in AI computing: AI chip compute grows "
    "3x every 2 years, but memory bandwidth only grows 1.6x. This is the Memory Wall problem. As "
    "compute density increases, more of a GPU's time is spent waiting for data than executing "
    "calculations."
))
story.append(body(
    "HBM (High Bandwidth Memory) is the solution. It stacks DRAM dies vertically and places them "
    "adjacent to the compute chip, dramatically reducing latency and increasing bandwidth. But HBM "
    "is expensive, capacity-constrained, and technically difficult to manufacture — only Samsung and "
    "SK Hynix (plus Micron) can produce HBM3E at scale."
))
story.append(spacer(0.05))
story.append(h2("Agentic AI Changes the Math"))
story.append(body(
    "Current LLMs: 1 prompt → 1 response → memory freed"
))
story.append(body(
    "Agentic AI: 1 task → 10–15 reasoning steps → persistent KV cache → memory held across "
    "entire task. Each reasoning step requires loading context, retrieving tools, and writing "
    "intermediate outputs — all memory bandwidth operations."
))
story.append(body(
    "SK Hynix management explicitly called out in their Q4 2025 call that demand continues to "
    "exceed supply even as output is maximized. This is before agentic AI even reaches mass deployment."
))
story.append(spacer(0.05))
story.append(h2("Supply-Demand Reality"))
demand_points = [
    "AI hyperscalers (Microsoft/OpenAI Stargate, Google, Meta, Amazon) are in an infrastructure arms race",
    "Stargate alone: 900,000 HBM wafers committed through SK Hynix",
    "Server DRAM contract prices up 60–70% from prior cycle lows",
    "S&P Global: Samsung's revenue per bit from conventional DRAM forecast to rise 116% YoY in 2026",
    "SK Hynix Q4 2025 operating margin: 58% — pricing power is real",
]
for pt in demand_points:
    story.append(bullet(pt))
story.append(spacer(0.1))
supply_points = [
    "Samsung and SK Hynix control ~90% of HBM capacity",
    "New fab construction: 2–3 year lead time minimum",
    "Existing capacity allocated to HBM means legacy DRAM supply tightening — conventional DDR5 also rising",
]
story.append(bold_body("Supply constraints:"))
for pt in supply_points:
    story.append(bullet(pt))
story.append(spacer(0.15))

# ── Valuation ────────────────────────────────────────────────────────────────
story.append(section_bar("VALUATION", ""))
story.append(spacer(0.1))
story.append(h2("Scenario Analysis"))
scen_data = [
    ["Scenario", "EWY Price", "Upside/Downside", "Probability", "Commentary"],
    ["Bear Case", "$100–$108", "-12% to -19%", "20%", "Cycle peaks early; geopolitical risk"],
    ["Base Case", "$145–$155", "+18% to +26%", "55%", "HBM supercycle proves durable"],
    ["Bull Case", "$165–$175", "+34% to +42%", "25%", "Agentic AI drives faster demand acceleration"],
]
t = Table(scen_data, colWidths=[1.0*inch, 1.0*inch, 1.3*inch, 0.9*inch, 2.3*inch])
t.setStyle(TableStyle([
    ('BACKGROUND',  (0,0), (-1,0), DARK_BG),
    ('TEXTCOLOR',   (0,0), (-1,0), white),
    ('FONTNAME',    (0,0), (-1,0), 'Helvetica-Bold'),
    ('FONTSIZE',    (0,0), (-1,-1), 8),
    ('ROWBACKGROUNDS', (0,1), (-1,-1), [LIGHT_BG, HexColor("#F0F4F8")]),
    ('BOX',         (0,0), (-1,-1), 0.5, GOLD_LIGHT),
    ('INNERGRID',   (0,0), (-1,-1), 0.3, GOLD_LIGHT),
    ('TOPPADDING', (0,0), (-1,-1), 4),
    ('BOTTOMPADDING',(0,0),(-1,-1), 4),
    ('LEFTPADDING', (0,0), (-1,-1), 5),
    ('ALIGN',       (1,0), (2,-1), 'CENTER'),
    ('TEXTCOLOR',   (0,1), (0,1), RED),
    ('TEXTCOLOR',   (0,2), (0,2), GREEN),
    ('TEXTCOLOR',   (0,3), (0,3), BLUE),
    ('FONTNAME',    (0,1), (0,3), 'Helvetica-Bold'),
]))
story.append(t)
story.append(spacer(0.08))
ev = 0.20*106 + 0.55*150 + 0.25*170
story.append(body(
    f"<b>Expected Value:</b> ${ev:.2f} — {((ev/EWY_CURRENT)-1)*100:.1f}% upside from ${EWY_CURRENT} "
    f"(weighted probability: Bear 20%, Base 55%, Bull 25%)"
))
story.append(spacer(0.1))
story.append(h2("Implied EWY P/E Multiples"))
pe_data = [
    ["Scenario", "EWY P/E", "Commentary"],
    ["Current", "16.5x", "Peak-cycle discount applied"],
    ["Bear", "13–14x", "Cycle peaks, multiples compress"],
    ["Base", "18–20x", "HBM supercycle proves durable, re-rating"],
    ["Bull", "22–25x", "Structural memory shortage confirmed"],
]
t = Table(pe_data, colWidths=[1.0*inch, 1.0*inch, 4.5*inch])
t.setStyle(TableStyle([
    ('BACKGROUND',  (0,0), (-1,0), BLUE),
    ('TEXTCOLOR',   (0,0), (-1,0), white),
    ('FONTNAME',    (0,0), (-1,0), 'Helvetica-Bold'),
    ('FONTSIZE',    (0,0), (-1,-1), 8),
    ('ROWBACKGROUNDS', (0,1), (-1,-1), [LIGHT_BG, HexColor("#F0F4F8")]),
    ('BOX',         (0,0), (-1,-1), 0.5, GOLD_LIGHT),
    ('INNERGRID',   (0,0), (-1,-1), 0.3, GOLD_LIGHT),
    ('TOPPADDING', (0,0), (-1,-1), 3),
    ('BOTTOMPADDING',(0,0),(-1,-1), 3),
    ('LEFTPADDING', (0,0), (-1,-1), 6),
]))
story.append(t)
story.append(spacer(0.15))

# ── Risk Assessment ──────────────────────────────────────────────────────────
story.append(section_bar("RISK ASSESSMENT", ""))
story.append(spacer(0.1))
risks = [
    ("Cyclical Peak Risk", "HIGH", "Legitimate — SK Hynix at 58% operating margins is historically extreme. "
     "Counterpoint: AI hyperscalers are signing long-term supply contracts, changing cycle dynamics vs. prior cycles."),
    ("Oil Price Sensitivity", "MEDIUM", "South Korea imports 70% of oil. High oil ($112) is a KRW headwind. "
     "However — chip exporters paid in USD benefit from weak KRW. Net effect on Samsung/SK Hynix is mixed."),
    ("Korean Won Weakness", "MEDIUM", "USD/KRW at 1,510 is elevated. Sharp reversal would reduce translated earnings. "
     "Risk cuts both ways — current levels partly reflect worst-case FX scenario."),
    ("Geopolitical / China Risk", "MEDIUM", "US export controls on advanced chips to China are ongoing. Both companies "
     "are diversifying capacity to Korea and US. Structural trend toward AI-memory independence from China is positive."),
    ("Concentration Risk", "LOW-MEDIUM", "Samsung + SK Hynix at 41% of fund. A manufacturing disaster at either "
     "company (yield problem, fire, earthquake) would directly damage the thesis."),
    ("Agentic AI Timeline Risk", "MEDIUM", "The 10–15x compute multiplier for agentic AI is an approximation. "
     "If agentic AI stalls or efficiency improvements offset compute increases, demand growth may not materialize as expected."),
]
risk_data = [[
    Paragraph(f"<b>{name}</b>", ParagraphStyle('rn', fontName='Helvetica-Bold', fontSize=8, textColor=DARK_BG)),
    Paragraph(f"<b>{level}</b>", ParagraphStyle('rl', fontName='Helvetica-Bold', fontSize=8,
               textColor=RED if level=="HIGH" else (HexColor("#E67E22") if level=="MEDIUM" else GREEN))),
    Paragraph(desc, ParagraphStyle('rd', fontName='Helvetica', fontSize=8, textColor=TEXT, leading=12)),
] for name, level, desc in risks]
t = Table(risk_data, colWidths=[1.5*inch, 0.6*inch, 4.4*inch])
t.setStyle(TableStyle([
    ('BOX',           (0,0), (-1,-1), 0.5, GOLD_LIGHT),
    ('INNERGRID',    (0,0), (-1,-1), 0.3, GOLD_LIGHT),
    ('BACKGROUND',    (0,0), (-1,-1), LIGHT_BG),
    ('TOPPADDING',   (0,0), (-1,-1), 5),
    ('BOTTOMPADDING',(0,0), (-1,-1), 5),
    ('LEFTPADDING',  (0,0), (-1,-1), 6),
    ('VALIGN',       (0,0), (-1,-1), 'TOP'),
]))
story.append(t)
story.append(spacer(0.15))

# ── Conclusion ───────────────────────────────────────────────────────────────
story.append(section_bar("CONCLUSION", ""))
story.append(spacer(0.1))
story.append(body(
    "The market is applying a cycle-peak discount to two companies reporting the strongest fundamental "
    "results in their corporate histories. SK Hynix posted 90% earnings growth and 58% operating margins. "
    "Samsung posted 155% earnings growth. Server DRAM prices are up 60–70%. HBM is in structural shortage "
    "with a 2–3 year lead time to add new capacity."
))
story.append(body(
    f"EWY at ${EWY_CURRENT}, 20% below its 52-week high of ${EWY_HIGH}, is pricing maximum pessimism "
    "about the memory cycle's durability. But the buyers signing long-term HBM supply contracts are "
    "not speculative — Microsoft, Google, Meta, and Amazon are building AI datacenters with 3–5 year "
    "infrastructure roadmaps."
))
story.append(body(
    "The 41% combined weight in Samsung and SK Hynix is not a bug — it is the thesis. A rising tide "
    "lifts these two, and they lift EWY with them."
))
story.append(spacer(0.1))
story.append(Paragraph(
    "★★★  SPECULATIVE BUY — 12-month horizon. Size accordingly.  ★★★",
    ParagraphStyle('rating', fontName='Helvetica-Bold', fontSize=11, textColor=GREEN,
                  alignment=TA_CENTER, spaceBefore=4, spaceAfter=4)
))
story.append(spacer(0.15))

# ── Disclaimer ──────────────────────────────────────────────────────────────
story.append(rule())
story.append(Paragraph(
    "This thesis is for educational and research purposes only. It is not financial advice. "
    "The author is an AI agent and not a licensed investment advisor. Always do your own research "
    "and consult a financial advisor before making investment decisions. Past performance does not "
    "guarantee future results. Data sourced from yfinance, StockAnalysis.com, Futurum Research, "
    "TrendForce, S&P Global Market Intelligence, and company disclosures.",
    ParagraphStyle('disc', fontName='Helvetica', fontSize=7, textColor=GRAY,
                  alignment=TA_JUSTIFY, leading=10)
))
story.append(spacer(0.05))
story.append(Paragraph(
    "📅 Thesis version 1.0 — April 4, 2026 — Analyst: Josiah Collins",
    ParagraphStyle('ver', fontName='Helvetica', fontSize=7, textColor=GRAY, alignment=TA_LEFT)
))

doc.build(story)
print(f"PDF written to: {OUTPUT_PATH}")
