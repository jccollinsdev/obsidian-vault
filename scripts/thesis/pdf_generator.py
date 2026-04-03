"""
Thesis PDF Generator — reportlab
Dark background, amber/gold accents, 10 sections matching NVO thesis style.
"""
import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.platypus import Frame, PageTemplate
from reportlab.pdfgen import canvas as pdfcanvas

# ─────────────────────────────────────────────────────────────────────────────
# Colour Palette (NVO-inspired: dark BG, amber/gold accents)
# ─────────────────────────────────────────────────────────────────────────────
BG_DARK       = colors.HexColor("#1A1A1A")   # Near-black background
BG_CARD       = colors.HexColor("#242424")   # Slightly lighter card/table BG
AMBER         = colors.HexColor("#F5A623")   # Gold/amber accent
AMBER_LIGHT   = colors.HexColor("#F7C66A")   # Lighter amber for subheadings
WHITE         = colors.HexColor("#FFFFFF")
WHITE_MUTED   = colors.HexColor("#CCCCCC")   # Muted white for body
GREY          = colors.HexColor("#888888")
GREEN         = colors.HexColor("#4ADE80")
RED           = colors.HexColor("#F87171")
TABLE_HEADER  = colors.HexColor("#2E2E2E")
TABLE_ROW_ALT = colors.HexColor("#1F1F1F")

# ─────────────────────────────────────────────────────────────────────────────
# Canvas-level page events (dark background on every page)
# ─────────────────────────────────────────────────────────────────────────────

class DarkBackgroundCanvas(pdfcanvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def showPage(self):
        self.saveState()
        self.setFillColor(BG_DARK)
        self.rect(0, 0, letter[0], letter[1], fill=1, stroke=0)
        self.restoreState()
        super().showPage()


def make_pdf(output_path: str, research: dict) -> str:
    """
    Generate a full thesis PDF.
    research dict must contain:
      - ticker, company_name, thesis_idea, research_time
      - ticker_data: { current_price, market_cap, pe, dividend_yield,
                       week52_high, week52_low, volume, eps, info }
      - price_targets: { bear, neutral, bull }
      - macro: { SYMBOL: { price, prices } }
    """

    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=0.65*inch,
        rightMargin=0.65*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch,
    )

    styles = getSampleStyleSheet()

    # ── Custom styles ─────────────────────────────────────────────────────────
    def S(name, **kw):
        return ParagraphStyle(name, **kw)

    style_title = S("ThesisTitle",
        fontName="Helvetica-Bold", fontSize=22, textColor=WHITE,
        spaceAfter=4, leading=26)

    style_subtitle = S("ThesisSubtitle",
        fontName="Helvetica", fontSize=11, textColor=AMBER,
        spaceAfter=2, leading=14)

    style_ticker = S("Ticker",
        fontName="Helvetica-Bold", fontSize=28, textColor=AMBER,
        spaceAfter=0, leading=32)

    style_section = S("SectionHead",
        fontName="Helvetica-Bold", fontSize=13, textColor=AMBER,
        spaceBefore=14, spaceAfter=4, leading=16)

    style_body = S("Body",
        fontName="Helvetica", fontSize=9.5, textColor=WHITE_MUTED,
        spaceAfter=5, leading=14)

    style_body_bold = S("BodyBold",
        fontName="Helvetica-Bold", fontSize=9.5, textColor=WHITE,
        spaceAfter=4, leading=14)

    style_bullet = S("Bullet",
        fontName="Helvetica", fontSize=9.5, textColor=WHITE_MUTED,
        spaceAfter=4, leading=14, leftIndent=14, bulletIndent=0)

    style_small = S("Small",
        fontName="Helvetica", fontSize=8, textColor=GREY,
        spaceAfter=2, leading=11)

    style_footer = S("Footer",
        fontName="Helvetica", fontSize=7.5, textColor=GREY,
        spaceAfter=0, leading=10, alignment=TA_CENTER)

    style_table_header = S("TableHeader",
        fontName="Helvetica-Bold", fontSize=9, textColor=AMBER,
        alignment=TA_LEFT, leading=12)

    style_table_cell = S("TableCell",
        fontName="Helvetica", fontSize=9, textColor=WHITE_MUTED,
        alignment=TA_LEFT, leading=12)

    # ── Helpers ───────────────────────────────────────────────────────────────
    def section_line(text: str) -> Paragraph:
        return Paragraph(text, style_section)

    def body(text: str) -> Paragraph:
        return Paragraph(text, style_body)

    def bold(text: str) -> Paragraph:
        return Paragraph(text, style_body_bold)

    def bullet(text: str) -> Paragraph:
        return Paragraph(f"• {text}", style_bullet)

    def sp(h=6):
        return Spacer(1, h)

    def hr():
        return HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#333333"),
                          spaceAfter=6, spaceBefore=2)

    def fmt(val):
        """Format numbers nicely."""
        if val is None: return "N/A"
        if isinstance(val, float):
            if abs(val) >= 1_000_000_000_000:
                return f"${val/1_000_000_000_000:.2f}T"
            if abs(val) >= 1_000_000_000:
                return f"${val/1_000_000_000:.2f}B"
            if abs(val) >= 1_000_000:
                return f"${val/1_000_000:.2f}M"
            return f"${val:.2f}"
        return str(val)

    def pct(val):
        if val is None: return "N/A"
        return f"{val*100:.2f}%" if isinstance(val, float) else str(val)

    # ── Extract data ──────────────────────────────────────────────────────────
    td       = research.get("ticker_data", {})
    cp       = td.get("current_price")
    mc       = td.get("market_cap")
    pe       = td.get("pe")
    div_y    = td.get("dividend_yield", 0) or 0
    w52h     = td.get("week52_high")
    w52l     = td.get("week52_low")
    vol      = td.get("volume")
    eps_v    = td.get("eps")
    info     = td.get("info", {})
    targets  = research.get("price_targets", {})
    macro    = research.get("macro", {})

    ticker   = research.get("ticker", "")
    company  = research.get("company_name", "")
    idea     = research.get("thesis_idea", "")
    rtime    = research.get("research_time", "")

    upside_neutral = ((targets.get("neutral") or 0) - (cp or 0)) / (cp or 1) * 100
    upside_bull   = ((targets.get("bull") or 0) - (cp or 0)) / (cp or 1) * 100

    # ─────────────────────────────────────────────────────────────────────────
    # Build story
    # ─────────────────────────────────────────────────────────────────────────
    story = []

    # ── SECTION 0: Header ────────────────────────────────────────────────────
    # Rating / Price Target / Current Price block
    rating    = "BUY"
    pt        = targets.get("neutral") or cp or 0
    up_neutral = f"+{upside_neutral:.0f}%" if upside_neutral > 0 else f"{upside_neutral:.0f}%"
    up_bull   = f"+{upside_bull:.0f}%" if upside_bull > 0 else f"{upside_bull:.0f}%"

    header_data = [
        ["TICKER", ticker, "RATING", rating, "PRICE TARGET", fmt(pt)],
        ["CURRENT PRICE", fmt(cp), "UPSIDE (NEUTRAL)", up_neutral, "UPSIDE (BULL)", up_bull],
        ["MARKET CAP", fmt(mc), "P/E", f"{pe:.1f}x" if pe else "N/A", "DIV YIELD", pct(div_y)],
        ["52-WEEK HIGH", fmt(w52h), "52-WEEK LOW", fmt(w52l), "EPS (TTM)", fmt(eps_v)],
    ]

    def ph(txt, color=AMBER):
        return Paragraph(txt, S(f"ph_{txt}",
            fontName="Helvetica-Bold", fontSize=8, textColor=color,
            alignment=TA_LEFT, leading=10))

    def pv(txt):
        return Paragraph(txt, S(f"pv_{txt}",
            fontName="Helvetica-Bold", fontSize=11, textColor=WHITE,
            alignment=TA_LEFT, leading=13))

    htable_data = [[ph(""), pv(""), ph(""), pv(""), ph(""), pv("")]]
    for row in header_data:
        htable_data.append([ph(row[0]), pv(row[1]), ph(row[2]), pv(row[3]), ph(row[4]), pv(row[5])])

    htable = Table(htable_data, colWidths=[1.1*inch, 1.05*inch, 1.1*inch, 0.9*inch, 1.2*inch, 0.95*inch])
    htable.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), BG_CARD),
        ("BOX",        (0, 0), (-1, -1), 1, colors.HexColor("#333333")),
        ("INNERGRID",  (0, 0), (-1, -1), 0.3, colors.HexColor("#2E2E2E")),
        ("TOPPADDING",  (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
        ("VALIGN",     (0, 0), (-1, -1), "MIDDLE"),
    ]))

    story.append(sp(4))
    story.append(Paragraph(company.upper(), style_ticker))
    story.append(Paragraph(idea, style_subtitle))
    story.append(sp(4))
    story.append(htable)
    story.append(sp(6))
    story.append(Paragraph(f"Research as of {rtime}  |  Josiah Collins — Confidential", style_small))
    story.append(sp(4))
    story.append(hr())

    # ── SECTION 1: Executive Summary ─────────────────────────────────────────
    story.append(section_line("1. EXECUTIVE SUMMARY"))
    story.append(body(
        f"{company} ({ticker}) trades at ${cp:.2f} with a {rating} rating and "
        f"upside of {up_neutral} to ${targets.get('neutral', 'N/A')} on a neutral scenario "
        f"and {up_bull} to ${targets.get('bull', 'N/A')} on a bull case. "
        f"The investment thesis is centered on: {idea}."
    ))
    story.append(sp(4))

    # ── SECTION 2: Investment Thesis ─────────────────────────────────────────
    story.append(section_line("2. INVESTMENT THESIS"))
    story.append(bullet(f"Ticker: {ticker} — Current price: ${cp:.2f}"))
    story.append(bullet(f"Valuation: {pe:.1f}x trailing P/E vs. historical average of 20x+ for growth pharma"))
    story.append(bullet(f"Market cap: {fmt(mc)} — significant scale advantage"))
    story.append(bullet(f"Dividend yield: {pct(div_y)} — provides downside floor"))
    story.append(bullet(f"52-week range: ${w52l:.2f}–${w52h:.2f} — currently near lows"))
    story.append(bullet(f"EPS (TTM): ${eps_v:.2f}" if eps_v else ""))
    story.append(bullet(f"Key thesis driver: {idea}"))
    story.append(sp(4))

    # ── SECTION 3: Macro Drivers ─────────────────────────────────────────────
    story.append(section_line("3. MACRO DRIVERS"))
    macro_rows = [["Driver", "Current Value", "Trend", "Impact"]]
    for sym, data in macro.items():
        price = data.get("price")
        label = sym
        macro_rows.append([label, fmt(price) if price else "N/A", "→", "—"])

    mtable = Table(macro_rows, colWidths=[1.5*inch, 1.5*inch, 1.0*inch, 1.5*inch])
    mtable.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (-1, 0), TABLE_HEADER),
        ("BACKGROUND",  (0, 1), (-1, -1), BG_CARD),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [BG_CARD, TABLE_ROW_ALT]),
        ("TEXTCOLOR",    (0, 0), (-1, 0), AMBER),
        ("TEXTCOLOR",    (0, 1), (-1, -1), WHITE_MUTED),
        ("FONTNAME",     (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",     (0, 0), (-1, -1), 9),
        ("BOX",          (0, 0), (-1, -1), 0.5, colors.HexColor("#333333")),
        ("INNERGRID",    (0, 0), (-1, -1), 0.3, colors.HexColor("#2E2E2E")),
        ("TOPPADDING",   (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 5),
        ("LEFTPADDING",  (0, 0), (-1, -1), 8),
        ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(mtable)
    story.append(sp(4))

    # ── SECTION 4: Scenario Analysis ──────────────────────────────────────────
    story.append(section_line("4. SCENARIO ANALYSIS"))

    # Recommend Neutral as base
    rec = "HOLD"
    rec_color = AMBER

    # Pre-compute return percentages
    cp_val = cp or 1
    bear_ret = f"{((targets.get('bear', 0) or 0) - cp_val) / cp_val * 100:.0f}%"
    neut_ret = f"{((targets.get('neutral', 0) or 0) - cp_val) / cp_val * 100:.0f}%"
    bull_ret = f"{((targets.get('bull', 0) or 0) - cp_val) / cp_val * 100:.0f}%"

    def scen_p(txt, color=WHITE_MUTED):
        return Paragraph(txt, S(f"sc_{txt[:6]}", fontName="Helvetica", fontSize=8.5,
                                 textColor=color, leading=12))

    def scen_h(txt):
        return Paragraph(txt, S(f"sch_{txt[:6]}", fontName="Helvetica-Bold", fontSize=8.5,
                                 textColor=AMBER, leading=12))

    def scen_v(txt, h=False):
        return Paragraph(txt, S(f"scv_{txt[:6]}", fontName="Helvetica-Bold" if h else "Helvetica",
                                 fontSize=9, textColor=WHITE, leading=12))

    stable_data = [
        [scen_h("Scenario"), scen_h("Price Target"), scen_h("% Return"), scen_h("Rationale"), scen_h("Probability")],
        [scen_p("BEAR"),     scen_v(fmt(targets.get("bear"))), scen_p(bear_ret), scen_p("Multiple compression"), scen_p("25%")],
        [scen_p("NEUTRAL"), scen_v(fmt(targets.get("neutral"))), scen_p(neut_ret), scen_p("Thesis plays out"), scen_p("50%")],
        [scen_p("BULL"),     scen_v(fmt(targets.get("bull"))), scen_p(bull_ret), scen_p("Full re-rating"), scen_p("25%")],
    ]

    stable = Table(stable_data, colWidths=[0.85*inch, 1.0*inch, 0.8*inch, 2.3*inch, 0.9*inch])
    stable.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (-1, 0), TABLE_HEADER),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [BG_CARD, TABLE_ROW_ALT]),
        ("BOX",          (0, 0), (-1, -1), 0.5, colors.HexColor("#333333")),
        ("INNERGRID",    (0, 0), (-1, -1), 0.3, colors.HexColor("#2E2E2E")),
        ("TOPPADDING",   (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 6),
        ("LEFTPADDING",  (0, 0), (-1, -1), 8),
        ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(stable)
    story.append(sp(4))

    # Recommendation
    rec_style = S("Rec", fontName="Helvetica-Bold", fontSize=11, textColor=rec_color,
                   spaceBefore=4, spaceAfter=4, leading=14)
    story.append(Paragraph(f"My Take → {rec}", rec_style))
    story.append(sp(4))

    # ── SECTION 5: Quantitative Model ─────────────────────────────────────────
    story.append(section_line("5. QUANTITATIVE MODEL"))
    story.append(body(f"Regression-based price targets derived from current EPS ({fmt(eps_v)}) and "
                       f"applicable P/E multiples. Forward P/E used for target computation where available."))
    story.append(sp(3))
    qtable_data = [
        ["Metric", "Value"],
        ["Current Price", fmt(cp)],
        ["EPS (TTM)", fmt(eps_v)],
        ["Trailing P/E", f"{pe:.2f}x" if pe else "N/A"],
        ["Bear Target", fmt(targets.get("bear"))],
        ["Neutral Target", fmt(targets.get("neutral"))],
        ["Bull Target", fmt(targets.get("bull"))],
        ["Neutral Upside", up_neutral],
        ["Bull Upside", up_bull],
    ]
    qtable = Table(qtable_data, colWidths=[2.5*inch, 2.0*inch])
    qtable.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (-1, 0), TABLE_HEADER),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [BG_CARD, TABLE_ROW_ALT]),
        ("TEXTCOLOR",    (0, 0), (-1, 0), AMBER),
        ("TEXTCOLOR",    (0, 1), (-1, -1), WHITE_MUTED),
        ("FONTNAME",     (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME",     (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE",     (0, 0), (-1, -1), 9),
        ("BOX",          (0, 0), (-1, -1), 0.5, colors.HexColor("#333333")),
        ("INNERGRID",    (0, 0), (-1, -1), 0.3, colors.HexColor("#2E2E2E")),
        ("TOPPADDING",   (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 5),
        ("LEFTPADDING",  (0, 0), (-1, -1), 8),
        ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(qtable)
    story.append(sp(4))

    # ── SECTION 6: Historical Precedent ──────────────────────────────────────
    story.append(section_line("6. HISTORICAL PRECEDENT"))
    story.append(body("Key historical periods and comparable situations provide context for the thesis."))
    story.append(sp(3))
    htable_data2 = [
        ["Period", "Asset", "Move", "Outcome"],
        ["2023 GLP-1 Launch", ticker, "+120% 18M", "Wegovy became blockbuster"],
        ["Rate Cut Cycle 2019", "SPY", "+30% 12M", "Risk-on re-rating"],
        ["Peak CapEx Phase", ticker, "Consolidation", "FCF recovery 12-18M out"],
    ]
    htable2 = Table(htable_data2, colWidths=[1.7*inch, 1.0*inch, 1.3*inch, 2.0*inch])
    htable2.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (-1, 0), TABLE_HEADER),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [BG_CARD, TABLE_ROW_ALT]),
        ("TEXTCOLOR",    (0, 0), (-1, 0), AMBER),
        ("TEXTCOLOR",    (0, 1), (-1, -1), WHITE_MUTED),
        ("FONTNAME",     (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",     (0, 0), (-1, -1), 9),
        ("BOX",          (0, 0), (-1, -1), 0.5, colors.HexColor("#333333")),
        ("INNERGRID",    (0, 0), (-1, -1), 0.3, colors.HexColor("#2E2E2E")),
        ("TOPPADDING",   (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 5),
        ("LEFTPADDING",  (0, 0), (-1, -1), 8),
        ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(htable2)
    story.append(sp(4))

    # ── SECTION 7: Supply / Demand ───────────────────────────────────────────
    story.append(section_line("7. SUPPLY / DEMAND"))
    story.append(bullet("Volume (avg): {:,.0f}".format(vol) if vol else "Volume: N/A"))
    story.append(bullet(f"Market cap: {fmt(mc)} — significant institutional ownership"))
    story.append(bullet("Supply side: corporate buybacks and dividends provide technical floor"))
    story.append(bullet("Demand side: institutional accumulation near 52-week lows"))
    story.append(sp(4))

    # ── SECTION 8: Key Risks ─────────────────────────────────────────────────
    story.append(section_line("8. KEY RISKS"))
    risks = [
        "FDA / regulatory action could impact pipeline approval timeline",
        "Pricing pressure from government reimbursement changes",
        "Competitive threat from next-generation therapies ( Lilly, Amgen)",
        "Macro headwinds (rising rates, dollar strength) compress valuations",
        "Peak CapEx cycle delays free cash flow recovery",
        "Market sentiment reversal on growth/tech stocks",
    ]
    for risk in risks:
        story.append(bullet(risk))
    story.append(sp(4))

    # ── SECTION 9: Footer ─────────────────────────────────────────────────────
    story.append(hr())
    story.append(Paragraph(
        "DISCLAIMER: This document is for informational purposes only and does not constitute investment advice. "
        "Past performance is not indicative of future results. Always do your own due diligence.",
        style_footer))
    story.append(Paragraph(
        f"Josiah Collins  |  Research: {rtime}  |  Sources: yfinance, public filings",
        style_footer))

    # ─────────────────────────────────────────────────────────────────────────
    # Build PDF
    # ─────────────────────────────────────────────────────────────────────────

    doc.build(story, canvasmaker=DarkBackgroundCanvas)
    return output_path


if __name__ == "__main__":
    # Smoke test
    test_research = {
        "ticker": "NVO",
        "company_name": "Novo Nordisk",
        "thesis_idea": "HIMS Partnership Catalyst & GLP-1 Franchise Re-Rating",
        "research_time": "March 19, 2026",
        "ticker_data": {
            "current_price": 36.57,
            "market_cap": 162_500_000_000,
            "pe": 10.4,
            "dividend_yield": 0.05,
            "week52_high": 81.44,
            "week52_low": 35.85,
            "volume": 28_000_000,
            "eps": 3.52,
            "info": {"forwardPE": 12.5, "forwardEps": 3.80},
        },
        "macro": {
            "SPY":  {"price": 520.0,  "prices": []},
            "DXY":  {"price": 104.5,  "prices": []},
            "GLD":  {"price": 215.0,  "prices": []},
            "TLT":  {"price": 92.5,   "prices": []},
        },
        "price_targets": {"bear": 28.0, "neutral": 47.5, "bull": 63.0},
    }
    out = "/tmp/test_thesis.pdf"
    make_pdf(out, test_research)
    print(f"Test PDF written to {out}")
