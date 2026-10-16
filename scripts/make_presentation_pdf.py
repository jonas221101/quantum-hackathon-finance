from __future__ import annotations

import json
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs" / "Quantum_Finance_Presentation.pdf"
FIGURES = ROOT / "results" / "canonical" / "figures"
SUMMARY = ROOT / "results" / "canonical" / "summary.json"


def image(path: Path, width: float = 23 * cm, height: float = 11 * cm) -> Image:
    item = Image(str(path))
    item.drawWidth = width
    item.drawHeight = height
    return item


def table(data: list[list[str]], widths: list[float] | None = None) -> Table:
    item = Table(data, colWidths=widths, repeatRows=1)
    item.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#17324d")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#b5c4d1")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#edf3f7")]),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 7),
                ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ]
        )
    )
    return item


def build_pdf() -> None:
    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
    styles = getSampleStyleSheet()
    title = ParagraphStyle(
        "PresentationTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=28,
        leading=34,
        textColor=colors.HexColor("#17324d"),
        alignment=TA_CENTER,
        spaceAfter=18,
    )
    heading = ParagraphStyle(
        "PresentationHeading",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=21,
        leading=25,
        textColor=colors.HexColor("#17324d"),
        spaceAfter=12,
    )
    body = ParagraphStyle(
        "PresentationBody",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=11,
        leading=16,
        spaceAfter=8,
    )
    small = ParagraphStyle(
        "PresentationSmall",
        parent=body,
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#415466"),
    )
    bullet = ParagraphStyle("PresentationBullet", parent=body, leftIndent=14, bulletIndent=3)

    doc = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=landscape(A4),
        rightMargin=1.5 * cm,
        leftMargin=1.5 * cm,
        topMargin=1.2 * cm,
        bottomMargin=1.2 * cm,
        title="A Defensible Quantum Allocation Decision",
        author="Quantum Hackathon Finance Team",
    )
    story: list[object] = []

    def slide_heading(text: str, subtitle: str | None = None) -> None:
        story.append(Paragraph(text, heading))
        if subtitle:
            story.append(Paragraph(subtitle, small))
        story.append(Spacer(1, 0.2 * cm))

    story.extend(
        [
            Spacer(1, 2.2 * cm),
            Paragraph("A defensible quantum allocation decision", title),
            Paragraph(
                "Keep or tilt? Sector choices for the German public Kapitalrente satellite sleeve",
                ParagraphStyle("CoverSub", parent=body, fontSize=16, leading=22, alignment=TA_CENTER),
            ),
            Spacer(1, 1.2 * cm),
            Paragraph(
                "A verified classical answer key, two QAOA representations, stress testing, "
                "holdout evaluation, and a human-readable Keep / Switch / Review decision.",
                ParagraphStyle("CoverText", parent=body, fontSize=13, leading=19, alignment=TA_CENTER),
            ),
            Spacer(1, 1.8 * cm),
            Paragraph("Important: quantum results use IBM's local Qiskit Aer simulator. No quantum advantage is claimed.", small),
            PageBreak(),
        ]
    )

    slide_heading("1. The decision")
    story.append(
        Paragraph(
            "At 31 December 2019, an investment committee must decide which three of six industries "
            "should form an equal-weight satellite tilt. The current holding is NoDur + Hlth + Utils; "
            "the proposal replaces NoDur with HiTec.",
            body,
        )
    )
    story.append(
        table(
            [
                ["Profile", "Decision", "Portfolio", "Reason"],
                ["Growth", "SWITCH", "HiTec + Hlth + Utils", "Stable across supplied stresses"],
                ["Balanced", "REVIEW", "Base case: HiTec + Hlth + Utils", "Flips under HiTec return stress"],
                ["Risk-sensitive", "KEEP", "NoDur + Hlth + Utils", "Risk rule and current tilt dominate"],
            ],
            [3.3 * cm, 3.0 * cm, 6.0 * cm, 12.5 * cm],
        )
    )
    story.append(PageBreak())

    slide_heading("2. Data and model boundaries")
    story.append(
        table(
            [
                ["Item", "Treatment"],
                ["Estimation window", "60 monthly observations, Jan 2015 – Dec 2019"],
                ["Holdout window", "Jan 2020 – Dec 2024; never used for the decision"],
                ["Universe", "NoDur, Manuf, Enrgy, HiTec, Hlth, Utils"],
                ["Decision space", "20 equal-weight portfolios: choose exactly 3 of 6"],
                ["Binding rules", "Exactly 3 holdings and mandate loss tolerance"],
                ["Preferences", "Return, variance, switching penalty, soft HiTec cap"],
            ],
            [6 * cm, 18.8 * cm],
        )
    )
    story.append(Spacer(1, 0.5 * cm))
    story.append(
        Paragraph(
            "The model is a challenge-sized satellite sleeve, not the complete pension portfolio. "
            "Mandate parameters are teaching assumptions, not legal requirements.",
            body,
        )
    )
    story.append(PageBreak())

    slide_heading("3. Exact classical answer key")
    story.append(
        Paragraph(
            "There are only C(6,3) = 20 candidate portfolios. We enumerate all of them, apply the "
            "objective and loss rule exactly, and use the result as the audit key for every quantum run.",
            body,
        )
    )
    story.append(image(FIGURES / "fig_risk_return.png", 22 * cm, 10.5 * cm))
    story.append(PageBreak())

    slide_heading("4. Why balanced is a Review case")
    story.append(
        table(
            [
                ["Scenario", "Growth", "Balanced", "Risk-sensitive"],
                ["Base", "HiTec + Hlth + Utils", "HiTec + Hlth + Utils", "NoDur + Hlth + Utils"],
                ["HiTec return stress", "HiTec + Hlth + Utils", "NoDur + Hlth + Utils", "NoDur + Hlth + Utils"],
                ["Covariance stress", "HiTec + Hlth + Utils", "HiTec + Hlth + Utils", "NoDur + Hlth + Utils"],
            ],
            [5 * cm, 6 * cm, 7 * cm, 7 * cm],
        )
    )
    story.append(Spacer(1, 0.5 * cm))
    story.append(
        Paragraph(
            "The balanced recommendation changes under a plausible technology return stress. "
            "That is not a failed model: it is evidence that the committee should review its belief "
            "about technology's future edge before switching.",
            body,
        )
    )
    story.append(image(FIGURES / "fig_decision_map.png", 18 * cm, 7 * cm))
    story.append(PageBreak())

    slide_heading("5. Where quantum fits")
    story.append(
        Paragraph(
            "We encode one binary variable per industry. A bitstring identifies the selected industries. "
            "The QAOA cost combines return, risk, switching, and the soft concentration preference.",
            body,
        )
    )
    story.append(
        table(
            [
                ["Baseline", "Rule-aware design"],
                ["X mixer with cardinality penalties", "Dicke-state initialization"],
                ["Invalid bitstrings can be sampled", "XY mixer preserves exactly three holdings"],
                ["Validity checked after measurement", "Cardinality preserved structurally"],
                ["Compared against exact enumeration", "Compared against exact enumeration"],
            ],
            [12 * cm, 12 * cm],
        )
    )
    story.append(Spacer(1, 0.5 * cm))
    story.append(
        Paragraph(
            "The circuits are simulated with IBM's local Qiskit Aer statevector simulator and shot-based "
            "sampling. This is not IBM Quantum cloud hardware execution.",
            body,
        )
    )
    story.append(PageBreak())

    slide_heading("6. Quantum results")
    story.append(image(FIGURES / "fig_qaoa_comparison.png", 22 * cm, 10.5 * cm))
    story.append(
        Paragraph(
            "Exact enumeration remains the verifier. We report optimum probability, valid-sample fraction, "
            "seed variation, and shot noise rather than claiming a speedup.",
            small,
        )
    )
    story.append(PageBreak())

    slide_heading("7. Robustness and hindsight")
    story.append(
        Paragraph(
            "The decision is tested under supplied return and covariance stresses, parameter changes, "
            "bootstrap resampling, and the held-out 2020–2024 period. The holdout is reported after the "
            "decision and is never used to select a portfolio.",
            body,
        )
    )
    story.append(image(FIGURES / "fig_bootstrap.png", 11 * cm, 8 * cm))
    story.append(image(FIGURES / "fig_holdout.png", 11 * cm, 8 * cm))
    story.append(PageBreak())

    slide_heading("8. Responsible conclusion")
    story.append(
        table(
            [
                ["Claim we make", "Claim we do not make"],
                ["The rule-aware QAOA encoding is checked against an exact answer key.", "Quantum advantage over classical enumeration"],
                ["The balanced decision is stress-sensitive and should be reviewed.", "Historical returns are forecasts"],
                ["The holdout period exposes model and estimation risk.", "This is a complete pension-portfolio recommendation"],
                ["A human investment committee remains responsible.", "The simulator is IBM hardware"],
            ],
            [12 * cm, 12 * cm],
        )
    )
    story.append(Spacer(1, 0.7 * cm))
    story.append(
        Paragraph(
            "Final message: Growth → Switch. Balanced → Review. Risk-sensitive → Keep. "
            "The value is transparent decision support, not a claim that quantum computing is already faster.",
            ParagraphStyle("Final", parent=body, fontSize=15, leading=21, textColor=colors.HexColor("#17324d")),
        )
    )
    story.append(PageBreak())

    slide_heading("9. Demo flow")
    for item in [
        "Open the Streamlit dashboard and select a mandate.",
        "Show the exact classical answer key and the Keep / Switch / Review framing.",
        "Point to the risk/return map and current-versus-recommended comparison.",
        "Show the scenario flip for Balanced.",
        "Enable IBM Aer QAOA and compare X-penalty with Dicke + XY.",
        "End with the holdout chart and the explicit limitation: no quantum advantage claim.",
    ]:
        story.append(Paragraph(item, bullet, bulletText="•"))
    story.append(Spacer(1, 0.8 * cm))
    story.append(Paragraph("Dashboard: http://127.0.0.1:8501", body))
    story.append(Paragraph("Repository: quantum-hackathon-finance / main", small))

    doc.build(story)
    print(OUTPUT)


if __name__ == "__main__":
    build_pdf()
