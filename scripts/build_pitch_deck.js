// Build the pitch deck (docs/deck/Pitch_Deck_30_10.pptx) from results/canonical/deck_data.json.
//
//   python scripts/export_deck_data.py          # numbers from the canonical run
//   npm install pptxgenjs@3.12.0                 # once (or set NODE_PATH to an existing install)
//   node scripts/build_pitch_deck.js [out.pptx]  # default: docs/deck/Pitch_Deck_30_10.pptx
//
// One design system: dark slides for the hook and the close, light slides for content. Every light slide has the
// same label, title, takeaway bar, source line and page number in the same place. Charts are native (editable).
const path = require("path");
const fs = require("fs");
const pptxgen = require("pptxgenjs");

const ROOT = path.resolve(__dirname, "..");
const DATA = JSON.parse(fs.readFileSync(path.join(ROOT, "results/canonical/deck_data.json"), "utf8"));
const ASSETS = path.join(ROOT, "docs/deck/assets");
const OUT = process.argv[2] || path.join(ROOT, "docs/deck/Pitch_Deck_30_10.pptx");

const THEME = {
  name: "Keep Review Switch",
  headFontFace: "Calibri",
  bodyFontFace: "Calibri",
  colors: {
    dk1: "0A192F", lt1: "FFFFFF", dk2: "334155", lt2: "F8FAFC",
    accent1: "2563EB", accent2: "EA580C", accent3: "059669", accent4: "D97706", accent5: "DC2626", accent6: "64748B",
    hlink: "2563EB", folHlink: "7C3AED",
  },
};
const COL = {
  navy: "0A192F", body: "334155", muted: "64748B", line: "E2E8F0", card: "F8FAFC", tint: "EFF6FF", sky: "93C5FD",
  blue: "2563EB", tech: "EA580C", grey: "94A3B8", slate: "475569", white: "FFFFFF",
  lena: "059669", thomas: "D97706", anna: "DC2626",
};
const SAVER = {
  lena: { name: "Lena", profile: "Growth", key: "growth", colour: COL.lena },
  thomas: { name: "Thomas", profile: "Balanced", key: "balanced", colour: COL.thomas },
  anna: { name: "Anna", profile: "Risk-sensitive", key: "risk_sensitive", colour: COL.anna },
};
const SOURCE_RUN = "Source: our canonical run (results/canonical) · data: Kenneth French, 6 US industries, Jan 2015–Dec 2019";
const pct = (v, d = 0) => `${(v * 100).toFixed(d)}%`;
const FONT = "+mn-lt";

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.333 x 7.5 in
pres.title = "Keep, review, or switch?";
pres.author = "Team Finance, TUM Quantum Hackathon 2026";
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };

// ------------------------------------------------------------------ layouts
const pageNumber = (colour) => ({ x: 12.25, y: 6.98, w: 0.6, h: 0.3, fontSize: 10, color: colour, align: "right" });
pres.defineSlideMaster({
  title: "DARK_TITLE",
  background: { color: COL.navy },
  objects: [
    { placeholder: { options: { name: "label", type: "body", x: 0.8, y: 1.2, w: 11.7, h: 0.4, fontSize: 14, bold: true,
                                color: COL.sky, charSpacing: 2 }, text: "" } },
    { placeholder: { options: { name: "title", type: "title", x: 0.8, y: 1.7, w: 11.7, h: 1.3, fontSize: 54, bold: true,
                                color: COL.white, align: "left", valign: "top" }, text: "" } },
  ],
});
pres.defineSlideMaster({
  title: "DARK",
  background: { color: COL.navy },
  objects: [
    { placeholder: { options: { name: "label", type: "body", x: 0.8, y: 0.9, w: 11.7, h: 0.4, fontSize: 14, bold: true,
                                color: COL.sky, charSpacing: 2 }, text: "" } },
    { placeholder: { options: { name: "title", type: "title", x: 0.8, y: 1.4, w: 11.7, h: 1.5, fontSize: 40, bold: true,
                                color: COL.white, align: "left", valign: "top" }, text: "" } },
  ],
  slideNumber: pageNumber(COL.muted),
});
pres.defineSlideMaster({
  title: "DARK_SPLIT",
  background: { color: COL.navy },
  objects: [
    { placeholder: { options: { name: "label", type: "body", x: 0.8, y: 0.9, w: 5.4, h: 0.4, fontSize: 14, bold: true,
                                color: COL.sky, charSpacing: 2 }, text: "" } },
    { placeholder: { options: { name: "title", type: "title", x: 0.8, y: 1.4, w: 5.4, h: 2.4, fontSize: 40, bold: true,
                                color: COL.white, align: "left", valign: "top" }, text: "" } },
  ],
  slideNumber: pageNumber(COL.muted),
});
pres.defineSlideMaster({
  title: "LIGHT",
  background: { color: COL.white },
  objects: [
    { placeholder: { options: { name: "label", type: "body", x: 0.6, y: 0.38, w: 12.1, h: 0.3, fontSize: 12, bold: true,
                                color: COL.blue, charSpacing: 2 }, text: "" } },
    { placeholder: { options: { name: "title", type: "title", x: 0.6, y: 0.68, w: 12.1, h: 0.75, fontSize: 30, bold: true,
                                color: COL.navy, align: "left", valign: "top" }, text: "" } },
    { placeholder: { options: { name: "source", type: "body", x: 0.6, y: 6.98, w: 11.4, h: 0.3, fontSize: 9,
                                color: COL.muted }, text: "" } },
  ],
  slideNumber: pageNumber(COL.muted),
});

// ------------------------------------------------------------------ building blocks
function dark(section, label, title, layout = "DARK") {
  const slide = pres.addSlide({ masterName: layout, sectionTitle: section });
  slide.addText(label, { placeholder: "label" });
  slide.addText(title, { placeholder: "title" });
  return slide;
}

function light(section, label, title, takeaway, source = SOURCE_RUN) {
  const slide = pres.addSlide({ masterName: "LIGHT", sectionTitle: section });
  slide.addText(label, { placeholder: "label" });
  slide.addText(title, { placeholder: "title" });
  slide.addText(source, { placeholder: "source" });
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.6, y: 6.2, w: 12.1, h: 0.62, fill: { color: COL.tint },
    line: { color: COL.tint }, rectRadius: 0.1, objectName: "Takeaway bar" });
  slide.addText([{ text: "Takeaway  ", options: { bold: true, color: COL.blue } }, { text: takeaway, options: { color: COL.navy } }],
    { x: 0.85, y: 6.2, w: 11.6, h: 0.62, fontSize: 18, valign: "middle", margin: 0, isTextBox: true, objectName: "Takeaway" });
  return slide;
}

function card(slide, x, y, w, h, border = COL.line, name = "Card") {
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, fill: { color: COL.card }, line: { color: border, width: border === COL.line ? 1 : 2.25 },
    rectRadius: 0.12, objectName: name });
}

function numberedCards(slide, items) {
  // items: [tag or "", head, body]; same geometry as every other three-card slide
  items.forEach(([tag, head, sub], i) => {
    const x = 0.6 + i * 4.1;
    card(slide, x, 1.65, 3.9, 4.3);
    slide.addShape(pres.shapes.OVAL, { x: x + 0.35, y: 2.0, w: 0.75, h: 0.75, fill: { color: COL.blue }, line: { color: COL.blue }, objectName: "Number" });
    text(slide, [{ text: String(i + 1), options: { color: COL.white, bold: true, fontSize: 24 } }], x + 0.35, 2.0, 0.75, 0.75,
      { align: "center", valign: "middle", name: "Number text" });
    if (tag) text(slide, [{ text: tag, options: { color: COL.muted, fontSize: 12, bold: true } }], x + 1.3, 2.2, 2.3, 0.35, { valign: "middle", name: "Tag" });
    text(slide, [{ text: head, options: { color: COL.navy, bold: true, fontSize: 24, breakLine: true, paraSpaceAfter: 10 } },
      { text: sub, options: { color: COL.body, fontSize: 20 } }], x + 0.35, 3.0, 3.2, 2.85, { name: "Card text" });
  });
}

function portrait(slide, who, x, y, size) {
  slide.addImage({ path: path.join(ASSETS, `${who}.jpg`), x, y, w: size, h: size, rounding: true,
    altText: `Illustrated portrait of ${SAVER[who].name}, one of our three example savers`, objectName: `Portrait ${SAVER[who].name}` });
  slide.addShape(pres.shapes.OVAL, { x, y, w: size, h: size, fill: { type: "none" }, line: { color: SAVER[who].colour, width: 2.5 },
    objectName: `Portrait ring ${SAVER[who].name}` });
}

function lines(items, opts = {}) {
  // items: strings (bullets) or {text, bold, colour, size, bullet}
  return items.map((it, i) => {
    const item = typeof it === "string" ? { text: it } : it;
    return { text: item.text, options: { bullet: item.bullet === false ? false : (opts.bullets !== false && item.bullet !== false ? { indent: 18 } : false),
      bold: !!item.bold, color: item.colour || COL.body, fontSize: item.size || opts.size || 18,
      breakLine: i < items.length - 1, paraSpaceAfter: opts.space ?? 10 } };
  });
}

function text(slide, runs, x, y, w, h, opts = {}) {
  slide.addText(runs, { x, y, w, h, valign: opts.valign || "top", align: opts.align || "left", margin: opts.margin ?? 0,
    fontFace: undefined, isTextBox: true, objectName: opts.name || "Text", fit: "none" });
}

const axisStyle = (extra = {}) => ({
  catAxisLabelColor: COL.body, valAxisLabelColor: COL.body, catAxisLabelFontSize: 12, valAxisLabelFontSize: 12,
  catAxisLabelFontFace: FONT, valAxisLabelFontFace: FONT, valGridLine: { color: COL.line, size: 0.75 },
  catGridLine: { style: "none" }, catAxisLineColor: COL.line, valAxisLineShow: false,
  legendFontFace: FONT, legendFontSize: 12, legendColor: COL.body, dataLabelFontFace: FONT, dataLabelFontSize: 12,
  dataLabelColor: COL.body, titleFontFace: FONT, ...extra,
});

// ------------------------------------------------------------------ slides
const V = DATA.verdicts, N = DATA.noise, Q = DATA.quantum.methods;
const cur = DATA.baskets.find((b) => b.holdings === DATA.current);
const pro = DATA.baskets.find((b) => b.holdings === DATA.proposal);

// 1 Title
pres.addSection({ title: "Hook" });
{
  const s = pres.addSlide({ masterName: "DARK_TITLE", sectionTitle: "Hook" });
  s.addText("TEAM FINANCE BROSITOS & BROSITAS · TUM QUANTUM HACKATHON 2026", { placeholder: "label" });
  s.addText("Keep, review, or switch?", { placeholder: "title" });
  text(s, [{ text: "How a rule-keeping quantum circuit helps Germany's new pension fund decide, saver by saver",
    options: { color: "E2E8F0", fontSize: 24 } }], 0.8, 3.05, 7.4, 1.2, { name: "Subtitle" });
  ["lena", "thomas", "anna"].forEach((who, i) => portrait(s, who, 8.75 + i * 1.45, 3.0, 1.25));
  text(s, [{ text: "Ahmed Mahmoud · Ivan · Jonas Sandelmann · Manyu · Mingzhi · Samarth Seth", options: { color: COL.sky, fontSize: 14, breakLine: true } },
    { text: "Final pitch · 30 October 2026", options: { color: COL.muted, fontSize: 14 } }], 0.8, 6.2, 11.7, 0.8, { name: "Team" });
  s.addNotes("Hi, we are Team Finance. Our question sounds simple: should a pension fund keep its portfolio, switch it, or wait? " +
    "We answer it for three people, Lena, Thomas and Anna, and we use a quantum circuit that cannot break the rules. " +
    "Every number in this talk comes from one reproducible run of our code.");
}

// 2 Inflation meme
{
  const s = dark("Hook", "THE CHALLENGE", "Inflation is burning our savings", "DARK_SPLIT");
  const fx = 6.55, fy = 1.4, fw = 6.2, fh = fw * 140 / 250;
  s.addImage({ path: path.join(ASSETS, "this_is_fine.gif"), x: fx, y: fy, w: fw, h: fh, altText: "This is fine meme: a dog in a burning room", objectName: "Meme" });
  const tag = (t, rx, ry, rw, rh, rot, size) => s.addText(t, { x: fx + rx * fw, y: fy + ry * fh, w: rw * fw, h: rh * fh, rotate: rot,
    fill: { color: COL.white }, color: "111111", bold: true, fontSize: size, align: "center", valign: "middle", margin: 2, isTextBox: true, objectName: "Meme label" });
  tag("INFLATION", 0.638, 0.386, 0.15, 0.08, 4, 12);
  tag("INFLATION", 0.046, 0.694, 0.19, 0.095, -16, 15);
  tag("INFLATION", 0.76, 0.84, 0.19, 0.095, 15, 15);
  tag("MY SAVINGS", 0.405, 0.6, 0.12, 0.11, 0, 10);
  text(s, lines(["Savings lose value every year", "Pensions alone will not be enough"], { size: 20 }).map((r) => ({ ...r, options: { ...r.options, color: "E2E8F0" } })),
    0.8, 3.9, 5.4, 1.5, { name: "Body" });
  s.addNotes("This is how many savers feel. Prices rise every year, and money in a bank account quietly loses value. " +
    "The statutory pension alone will not close that gap.");
}

// 3 Doener index
{
  const s = dark("Hook", "THE DÖNER INDEX", "€100 today buys about €76 of goods in 2035, and €48 in 2050", "DARK_SPLIT");
  const ph = 5.4, pw = ph * 500 / 573, px = 12.75 - pw, py = 1.4;
  s.addImage({ path: path.join(ASSETS, "doner_index.jpg"), x: px, y: py, w: pw, h: ph,
    altText: "Two film stills: a full table in 2016 and a nearly empty one in 2026", objectName: "Photo" });
  const cap = (t, rel) => s.addText(t, { x: px + pw - 2.15, y: py + rel * ph, w: 2.05, h: 0.42, fill: { color: "F5F1E8" }, color: "111111",
    bold: true, fontSize: 16, align: "center", valign: "middle", margin: 0, isTextBox: true, objectName: "Caption" });
  cap("With €20 in 2016", 0.405);
  cap("With €20 in 2026", 0.9);
  text(s, [{ text: "If prices rise 3% a year and savings earn 0%.", options: { color: COL.sky, fontSize: 18 } }], 0.8, 4.0, 5.6, 0.8, { name: "Assumption" });
  s.addNotes("Our Döner index makes it concrete. If prices rise three percent a year and your savings earn nothing, " +
    "100 euros buys about 76 euros' worth of goods in 2035 and about 48 in 2050. Saving alone cannot fund a pension.");
}

// 4 Opportunity
{
  const s = dark("Hook", "THE OPPORTUNITY", "We saw an opportunity", "DARK_SPLIT");
  s.addImage({ path: path.join(ASSETS, "opportunity.jpg"), x: 6.55, y: 1.4, w: 6.2, h: 6.2 * 477 / 848, altText: "Disaster girl meme", objectName: "Meme" });
  text(s, lines(["Germany is building a capital-funded pension", "Someone has to decide how to invest it"], { size: 20 })
    .map((r) => ({ ...r, options: { ...r.options, color: "E2E8F0" } })), 0.8, 3.0, 5.4, 1.6, { name: "Body" });
  s.addNotes("Where others see a fire, we saw an opportunity. Germany is building a new, capital-funded pension. " +
    "Someone has to decide how that money is invested, and that is where we come in.");
}

// 5 Disclaimer
{
  const s = dark("Hook", "DISCLAIMER", "We are students, not your financial advisers");
  text(s, [{ text: "This is a teaching model, not financial advice. If it were, our own portfolios wouldn't be this red. ⚠️",
    options: { color: "E2E8F0", fontSize: 24 } }], 0.8, 3.1, 11.0, 1.4, { name: "Body" });
  s.addNotes("A quick disclaimer: this is a teaching model, not financial advice. If it were, our own portfolios would look better.");
}

// 6 Client
{
  const s = dark("Hook", "OUR CLIENT", "The investment committee of Germany's new pension fund");
  const stats = [["2%", "of gross wages go into a public fund"], ["2028", "the year it starts"], ["0", "guarantees: losses hit savers"]];
  stats.forEach(([big, small], i) => {
    const x = 0.8 + i * 4.0;
    text(s, [{ text: big, options: { color: COL.sky, fontSize: 60, bold: true, breakLine: true } },
      { text: small, options: { color: "E2E8F0", fontSize: 18 } }], x, 3.2, 3.6, 2.0, { name: "Stat" });
  });
  text(s, [{ text: "Its independent committee decides how the money is invested. We help it with one decision.",
    options: { color: COL.sky, fontSize: 18 } }], 0.8, 5.6, 11.7, 0.6, { name: "Body" });
  s.addNotes("Our client is the investment committee of the planned public fund for the Kapitalrente. From 2028, two percent of gross wages " +
    "go into this fund, with no guarantees. The committee decides how the money is invested, and we help it with one specific decision.");
}

// 7 Pink Panther (transition)
{
  const s = pres.addSlide({ masterName: "DARK", sectionTitle: "Hook" });
  s.addImage({ path: path.join(ASSETS, "pink_panther.gif"), x: 2.67, y: 1.15, w: 8.0, h: 6.0, sizing: { type: "crop", x: 0, y: 0, w: 8.0, h: 5.2 }, altText: "Pink Panther painting a wall", objectName: "GIF" });
  s.addNotes("So let's paint the picture of what we actually built.");
}

// 8 Challenge
pres.addSection({ title: "Problem" });
{
  const s = light("Problem", "THE CHALLENGE", "Savers need growth, but cannot afford big losses",
    "Change a pension portfolio only when the evidence is strong.", "Source: Alterssicherungskommission (June 2026)");
  card(s, 0.6, 1.65, 5.9, 4.3);
  card(s, 6.8, 1.65, 5.9, 4.3);
  text(s, [{ text: "What savers want", options: { bold: true, color: COL.navy, fontSize: 26, breakLine: true, paraSpaceAfter: 14 } },
    ...lines(["Growth that beats inflation", "Safety from big losses", "A sensible default if they never choose"], { size: 22, space: 14 })],
  1.0, 2.1, 5.1, 3.6, { name: "Card text" });
  text(s, [{ text: "Our questions", options: { bold: true, color: COL.blue, fontSize: 26, breakLine: true, paraSpaceAfter: 14 } },
    ...lines(["Is tech worth the extra risk?", "Do losses stay within each saver's limit?", "Who protects people who never choose?"], { size: 22, space: 14 })],
  7.2, 2.1, 5.1, 3.6, { name: "Card text" });
  s.addNotes("Savers want two things at once: growth that beats inflation, and safety from big losses. Many never choose a profile at all. " +
    "So our questions are: is a tech tilt worth the risk, do losses stay within each saver's limit, and who protects the people who never choose?");
}

// 9 Setup
{
  const s = light("Problem", "THE SETUP", "We decide one small slice: 3 of 6 sectors",
    "A small, checkable decision. We claim no quantum advantage.");
  const tiles = [["90%", "Core: a broad global index", "We don't touch it.", COL.navy],
    [pct(DATA.satellite_share), "Satellite: 3 of 6 US sectors", "Equal thirds of staples, manufacturing, energy, tech, health, utilities.", COL.blue],
    [String(DATA.baskets.length), "possible baskets", "A laptop checks all of them: our exact answer key.", COL.navy]];
  tiles.forEach(([big, head, sub, colour], i) => {
    const x = 0.6 + i * 4.1;
    card(s, x, 1.65, 3.9, 4.3);
    text(s, [{ text: big, options: { color: colour, fontSize: 72, bold: true, breakLine: true } },
      { text: head, options: { color: COL.navy, fontSize: 22, bold: true, breakLine: true, paraSpaceAfter: 8 } },
      { text: sub, options: { color: COL.body, fontSize: 18 } }], x + 0.35, 2.1, 3.2, 3.7, { name: "Tile text" });
  });
  s.addNotes("The fund's core is a broad global index; we do not touch it. We decide only the satellite, ten percent: which three of six " +
    "US sectors to hold, in equal thirds. That gives just twenty possible baskets, so a laptop finds the exact answer instantly. " +
    "We use that exact answer to grade our quantum circuit, and we claim no quantum advantage.");
}

// 10 Savers
{
  const s = light("Problem", "THE SAVERS", "Three savers, three different loss limits",
    "Thomas never chose a profile, so he deserves extra care.");
  const info = { lena: ["“I can handle big swings.”", "8%"], thomas: ["“I never chose a profile.”", "5%"],
    anna: ["“I can't afford big losses.”", "3%"] };
  ["lena", "thomas", "anna"].forEach((who, i) => {
    const x = 0.6 + i * 4.1, sv = SAVER[who];
    card(s, x, 1.65, 3.9, 4.3, sv.colour, `Card ${sv.name}`);
    portrait(s, who, x + 1.25, 1.85, 1.4);
    text(s, [{ text: `${sv.name.toUpperCase()} | ${sv.profile}`, options: { bold: true, color: sv.colour, fontSize: 20, breakLine: true } },
      { text: info[who][0], options: { italic: true, color: COL.muted, fontSize: 19, breakLine: true, paraSpaceAfter: 12 } },
      { text: `Loses more than ${info[who][1]} in at most ${DATA.allowed} of 60 months`, options: { color: COL.body, fontSize: 19 } }],
    x + 0.3, 3.45, 3.3, 2.4, { align: "center", name: "Card text" });
  });
  s.addNotes("Meet our savers. Lena chose growth and can handle big swings. Anna chose risk-sensitive and cannot afford big losses. " +
    "Thomas never chose, so he lands in balanced, our default. Each has a binding loss limit: a bad month may happen in at most six of sixty months. " +
    "Thomas matters most, because he never made a choice.");
}

// 11 Proposal
{
  const s = light("Problem", "THE PROPOSAL · GRANDMA'S BASKET OR NVIDIA'S?", "Swap staples for tech: more return, but more risk",
    "Is the extra return worth the extra risk? It depends on the saver.");
  const xs = DATA.baskets.map((b) => b.vol);
  const pick = (h) => DATA.baskets.map((b) => (b.holdings === h ? b.mean : null));
  const others = DATA.baskets.map((b) => (b.holdings === DATA.current || b.holdings === DATA.proposal ? null : b.mean));
  s.addChart(pres.charts.SCATTER, [
    { name: "Risk", values: xs },
    { name: "Other baskets", values: others },
    { name: "Today: staples + health + utilities", values: pick(DATA.current) },
    { name: "Proposal: tech + health + utilities", values: pick(DATA.proposal) },
  ], { x: 0.6, y: 1.6, w: 7.4, h: 4.45, lineSize: 0, lineDataSymbol: "circle", lineDataSymbolSize: 11,
    chartColors: ["CBD5E1", COL.blue, COL.tech], showLegend: true, legendPos: "b",
    showValAxisTitle: true, valAxisTitle: "Average monthly return (%)", showCatAxisTitle: true, catAxisTitle: "Risk: monthly volatility (%)",
    valAxisTitleColor: COL.body, catAxisTitleColor: COL.body, valAxisTitleFontSize: 12, catAxisTitleFontSize: 12,
    valAxisMinVal: 0.4, valAxisMaxVal: 1.15, catAxisMinVal: 2.6, catAxisMaxVal: 4.4, valAxisLabelFormatCode: "0.0", catAxisLabelFormatCode: "0.0",
    ...axisStyle(), objectName: "Risk-return chart", altText: "All 20 baskets by risk and return; today's basket has the lowest risk." });
  card(s, 8.3, 1.65, 4.4, 4.3);
  text(s, [{ text: "The proposal", options: { bold: true, color: COL.navy, fontSize: 24, breakLine: true, paraSpaceAfter: 12 } },
    ...lines([`Return: ${cur.mean.toFixed(2)}% → ${pro.mean.toFixed(2)}% a month`, `Risk: ${cur.vol.toFixed(2)}% → ${pro.vol.toFixed(2)}% a month`,
      "Today's basket: lowest risk of all 20", "No return can buy a breach of a loss limit"], { size: 19, space: 12 })], 8.65, 2.05, 3.8, 3.8, { name: "Card text" });
  s.addNotes("Today the satellite holds consumer staples, healthcare and utilities: the blue dot, the lowest risk of all twenty baskets. " +
    `The proposal swaps staples for tech, the orange dot: about ${(pro.mean - cur.mean).toFixed(2)} points more return a month, but more swings. ` +
    "Our rule: no extra return can ever buy a breach of a loss limit.");
}

// 12 How we decide
pres.addSection({ title: "Results" });
{
  const s = light("Results", "HOW WE DECIDE", "Rules first, then the evidence decides",
    "The burden of proof is on the change.", "Source: src/qhf/decision.py · 3 test settings: base case, tech earns 0.5 points less, sectors move more together");
  numberedCards(s, [["", "Check the loss limit", "Baskets that break it are out. No return buys them back."],
    ["", "Score the rest", "More return is good, more swings are bad, weighted per saver."],
    ["", "Switch only on strong evidence", "Same winner in all 3 test settings and in at least 70% of 500 replays. Otherwise: review, and hold."]]);
  s.addNotes("How do we decide? Step one: check each saver's loss limit; baskets that break it are out. Step two: score the rest, return against swings, " +
    "weighted for each saver. Step three: we only switch if the same basket wins in all three test settings and in at least seventy percent " +
    "of five hundred replays of history. Otherwise the answer is review: hold, and let the committee decide.");
}

// 13 Results overview
{
  const s = light("Results", "RESULTS", "One proposal, three answers", "“Review” is a valid answer, not a failure.");
  const res = { lena: ["SWITCH", `Better in ${pct(V.growth.bootstrap_candidate_beats_current)} of 500 replays`, "Wins every stress test"],
    thomas: ["REVIEW", "Near-tie: flips under stress", "Hold until the committee decides"],
    anna: ["KEEP", "Lowest risk of all 20 baskets", "Tech sits right on her loss limit"] };
  ["lena", "thomas", "anna"].forEach((who, i) => {
    const x = 0.6 + i * 4.1, sv = SAVER[who];
    card(s, x, 1.65, 3.9, 4.3, sv.colour, `Card ${sv.name}`);
    portrait(s, who, x + 1.35, 1.85, 1.2);
    text(s, [{ text: `${sv.name.toUpperCase()} | ${sv.profile}`, options: { bold: true, color: sv.colour, fontSize: 18, breakLine: true } },
      { text: res[who][0], options: { bold: true, color: sv.colour, fontSize: 48, breakLine: true } },
      { text: res[who][1], options: { color: COL.body, fontSize: 18, breakLine: true, paraSpaceAfter: 6 } },
      { text: res[who][2], options: { color: COL.body, fontSize: 18 } }], x + 0.25, 3.2, 3.4, 2.65, { align: "center", name: "Card text" });
  });
  s.addNotes("One proposal, three answers. Lena switches: the tech basket wins in every test and in eighty-nine percent of replays. " +
    "Anna keeps: her basket has the lowest risk, and tech sits right on her loss limit. Thomas gets review: it is a near-tie that flips under stress, " +
    "so we hold until the committee decides. Review is a legitimate answer, not a failure.");
}

function storyCard(s, who, head, items) {
  const sv = SAVER[who];
  card(s, 8.3, 1.65, 4.4, 4.3, sv.colour, `Card ${sv.name}`);
  portrait(s, who, 9.9, 1.85, 1.2);
  text(s, [{ text: head, options: { bold: true, color: sv.colour, fontSize: 28, breakLine: true, paraSpaceAfter: 8 } }, ...lines(items, { size: 18, space: 8 })],
    8.65, 3.2, 3.8, 2.7, { name: "Card text" });
}

// 14 Lena
{
  const s = light("Results", "LENA", "Lena: switching to tech wins every test", "Strong evidence → switch.");
  const H = DATA.lena_hist;
  const labels = H.centres.map((c) => String(c));
  s.addChart(pres.charts.BAR, [
    { name: "Tech basket better", labels, values: H.centres.map((c, i) => (c > 0 ? H.counts[i] : 0)) },
    { name: "Today's basket better", labels, values: H.centres.map((c, i) => (c > 0 ? 0 : H.counts[i])) },
  ], { x: 0.6, y: 1.6, w: 7.4, h: 4.45, barDir: "col", barGrouping: "stacked", barGapWidthPct: 15, chartColors: [COL.tech, COL.blue],
    showLegend: true, legendPos: "t", showValAxisTitle: true, valAxisTitle: "Replays (of 500)", showCatAxisTitle: true,
    catAxisTitle: "How much better the tech basket scores (bp a month)", valAxisTitleColor: COL.body, catAxisTitleColor: COL.body,
    valAxisTitleFontSize: 12, catAxisTitleFontSize: 12, catAxisLabelFrequency: 3, showTitle: true,
    title: `Tech basket better in ${pct(H.share_better)} of 500 replays`, titleColor: COL.navy, titleFontSize: 16,
    ...axisStyle(), objectName: "Lena replays chart", altText: `500 replays for Lena: the tech basket scores better in ${pct(H.share_better)}.` });
  storyCard(s, "lena", "Switch", [`+${(pro.mean - cur.mean).toFixed(2)} points return a month`, `Better in ${pct(V.growth.bootstrap_candidate_beats_current)} of 500 replays`,
    "Wins every stress test", "One-off switching cost earned back within a month"]);
  s.addNotes("For Lena we replayed the sixty months of history five hundred times. In eighty-nine percent of those replays the tech basket scores better, " +
    "and it wins in every stress test. It adds about 0.29 points of return a month, and the one-off switching cost is earned back within a month. " +
    "Strong evidence, so: switch.");
}

// 15 Thomas: number line
{
  const s = light("Results", "THOMAS", "Thomas: the data cannot tell the two baskets apart", "Too close to call → hold, and let the committee decide.");
  const x0 = 1.0, x1 = 7.6, lo = -1.2, hi = 1.2, axisY = 4.75;
  const X = (v) => x0 + (v - lo) / (hi - lo) * (x1 - x0);
  text(s, [{ text: "How much tech's monthly return may change before Thomas's answer flips", options: { color: COL.navy, bold: true, fontSize: 16 } }],
    0.6, 1.7, 7.4, 0.4, { name: "Chart title" });
  s.addShape(pres.shapes.RECTANGLE, { x: X(-N.se), y: axisY - 1.0, w: X(N.se) - X(-N.se), h: 1.0, fill: { color: COL.line }, line: { color: COL.line }, objectName: "Noise band" });
  text(s, [{ text: "Uncertainty of the estimate", options: { color: COL.body, fontSize: 13, breakLine: true } },
    { text: `\u00b1${N.se.toFixed(2)} points`, options: { color: COL.body, fontSize: 13, bold: true } }],
  X(N.se) - 2.45, axisY - 0.92, 2.35, 0.6, { align: "right", name: "Band label" });
  s.addShape(pres.shapes.LINE, { x: x0, y: axisY, w: x1 - x0, h: 0, line: { color: COL.navy, width: 1.5 }, objectName: "Axis" });
  [-1, -0.5, 0, 0.5, 1].forEach((v) => {
    s.addShape(pres.shapes.LINE, { x: X(v), y: axisY, w: 0, h: 0.1, line: { color: COL.navy, width: 1 }, objectName: "Tick" });
    const label = v === 0 ? [{ text: "0", options: { color: COL.navy, fontSize: 12, bold: true, breakLine: true } },
      { text: `today: ${N.hitec_mean.toFixed(2)}%`, options: { color: COL.navy, fontSize: 12, bold: true } }]
      : [{ text: (v > 0 ? "+" : "\u2212") + Math.abs(v).toFixed(1), options: { color: COL.body, fontSize: 12 } }];
    text(s, label, X(v) - 0.7, axisY + 0.12, 1.4, 0.45, { align: "center", name: "Tick label" });
  });
  text(s, [{ text: "Change in tech's expected return (points a month)", options: { color: COL.body, fontSize: 12 } }], x0, axisY + 0.62, x1 - x0, 0.3, { align: "center", name: "Axis title" });
  // Leftmost marker gets the lowest label row, so no label crosses another marker's line.
  const marker = (v, colour, label, rowY, opts = {}) => {
    s.addShape(pres.shapes.LINE, { x: X(v), y: rowY + 0.15, w: 0, h: axisY - rowY - 0.15, line: { color: colour, width: 2, dashType: opts.dash ? "dash" : "solid" }, objectName: "Marker" });
    s.addShape(pres.shapes.OVAL, { x: X(v) - 0.1, y: axisY - 0.1, w: 0.2, h: 0.2, fill: { color: colour }, line: { color: COL.white }, objectName: "Marker dot" });
    text(s, [{ text: label, options: { color: colour, fontSize: opts.size || 13, bold: !!opts.bold } }], 0.6, rowY, X(v) - 0.7, 0.3, { align: "right", name: "Marker label" });
  };
  marker(N.thomas_flip, COL.thomas, `Thomas flips at \u2212${Math.abs(N.thomas_flip).toFixed(2)}`, axisY - 2.45, { bold: true, size: 15 });
  marker(N.stress, COL.anna, `Stress test: \u2212${Math.abs(N.stress).toFixed(2)}`, axisY - 1.95, { dash: true });
  marker(N.lena_flip, COL.lena, `Lena flips at \u2212${Math.abs(N.lena_flip).toFixed(2)}`, axisY - 1.45, { dash: true });
  storyCard(s, "thomas", "Review", [`Lead: only ${N.thomas_lead_bp.toFixed(0)} bp a month`, `Flips if tech earns ${Math.abs(N.thomas_flip).toFixed(2)} less`,
    `Estimate wobbles by \u00b1${N.se.toFixed(2)}`, `Stress test (\u2212${Math.abs(N.stress).toFixed(1)}) flips it`]);
  s.addNotes(`For Thomas the tech basket is ahead by only ${N.thomas_lead_bp.toFixed(0)} basis points a month. Tech's expected return of ${N.hitec_mean.toFixed(2)} percent is an estimate ` +
    `from sixty months, and it could easily be ${N.se.toFixed(2)} points higher or lower: the grey band. Thomas's answer flips if tech earns just ${Math.abs(N.thomas_flip).toFixed(2)} points less, ` +
    "well inside that band, and the organisers' own stress test is already beyond it. The data cannot tell the two baskets apart, so we hold and let the committee decide.");
}

// 16 Anna
{
  const s = light("Results", "ANNA", "Anna: today's basket is the safer choice", "Safety first → keep.");
  const L = DATA.loss_months.risk_sensitive;
  const labels = ["2015–19 data", "Tech −0.5 pt", "Sectors move together", "Real 2020–24"];
  s.addChart([
    { type: pres.charts.BAR, data: [{ name: "Today's basket", labels, values: L.current }, { name: "Tech basket", labels, values: L.proposal }],
      options: { barGrouping: "clustered", chartColors: [COL.blue, COL.tech], barGapWidthPct: 60, showValue: true, dataLabelPosition: "outEnd" } },
    { type: pres.charts.LINE, data: [{ name: `Limit: at most ${DATA.allowed} of 60`, labels, values: labels.map(() => DATA.allowed) }],
      options: { chartColors: [COL.anna], lineSize: 2, lineDash: "dash", lineDataSymbol: "none" } },
  ], { x: 0.6, y: 1.6, w: 7.4, h: 4.45, showLegend: true, legendPos: "t", showValAxisTitle: true, valAxisTitle: "Months losing more than 3% (of 60)",
    valAxisTitleColor: COL.body, valAxisTitleFontSize: 12, valAxisMinVal: 0, valAxisMaxVal: 14, showTitle: true, title: "Anna's loss months by test setting",
    titleColor: COL.navy, titleFontSize: 16, ...axisStyle(), objectName: "Anna loss months chart",
    altText: "Anna's loss months: today's basket 5, 5, 5, 12; tech basket 6, 7, 9, 12; at most 6 allowed." });
  storyCard(s, "anna", "Keep", ["Lowest risk of all 20 baskets", `Tech sits on her limit: ${L.proposal[0]} of 60`,
    `Fails both stress tests: ${L.proposal[1]} and ${L.proposal[2]}`]);
  s.addNotes("For Anna, safety comes first. Her basket has the lowest risk of all twenty. The tech basket loses more than three percent in exactly six of sixty months, " +
    "the most her rule allows, and it breaks her limit in both stress tests. So: keep. The last bars show 2020 to 2024, which we never used to decide; we come back to that.");
}

// 17 Quantum circuit
pres.addSection({ title: "Quantum" });
{
  const s = light("Quantum", "OUR QUANTUM CIRCUIT", "Our quantum circuit can only suggest legal baskets",
    "The rule is built into the circuit, not punished afterwards.", "Method: Hadfield et al. (2019), QAOA with Dicke start and XY mixer · code: src/qhf/circuits.py");
  const rows = [["Organisers' penalty circuit", COL.slate, ["Start: all 64 patterns (44 illegal)", "Score + penalty", "X mixer: flips sectors on/off", "Measure: illegal answers possible"], [0, 3]],
    ["Our rule-keeping circuit", COL.blue, ["Start: only the 20 legal baskets", "Score: return vs risk", "XY mixer: swaps sectors, always 3", "Measure: only legal answers"], []]];
  rows.forEach(([title, colour, steps, bad], r) => {
    const y = 1.75 + r * 2.15;
    text(s, [{ text: title, options: { bold: true, color: colour, fontSize: 17 } }], 0.6, y, 7.4, 0.35, { name: "Row title" });
    steps.forEach((step, k) => {
      const x = 0.6 + k * 1.88, isBad = bad.includes(k);
      s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: y + 0.45, w: 1.65, h: 1.15, rectRadius: 0.08,
        fill: { color: isBad ? "FEF2F2" : (r ? COL.tint : COL.card) }, line: { color: isBad ? COL.anna : colour, width: 1.5 }, objectName: "Step box" });
      text(s, [{ text: step, options: { color: COL.navy, fontSize: 14 } }], x + 0.08, y + 0.45, 1.49, 1.15, { align: "center", valign: "middle", name: "Step label" });
      if (k < 3) s.addShape(pres.shapes.LINE, { x: x + 1.67, y: y + 1.02, w: 0.19, h: 0, line: { color: COL.muted, width: 1.5, endArrowType: "triangle" }, objectName: "Arrow" });
    });
  });
  text(s, [{ text: "Both repeat score and mix in 3 layers; a laptop tunes the dials.", options: { color: COL.muted, fontSize: 13 } }], 0.6, 5.65, 7.4, 0.35, { name: "Note" });
  card(s, 8.3, 1.65, 4.4, 4.3, COL.blue, "Card");
  text(s, [{ text: "Our idea", options: { bold: true, color: COL.blue, fontSize: 24, breakLine: true } },
    ...lines(["Start with the 20 legal baskets only", "Mix by swapping sectors: always exactly 3", "Illegal baskets never appear"], { size: 20, space: 14 })],
  8.65, 2.05, 3.8, 3.8, { name: "Card text" });
  s.addNotes("Now the quantum part. The usual approach, which the organisers used, starts with all sixty-four on-off patterns, including illegal ones, " +
    "and only punishes rule breaks with a penalty. Our circuit starts with the twenty legal baskets only, and its mixer swaps one sector for another, " +
    "so every basket always keeps exactly three sectors. Illegal answers cannot appear at all.");
}

// 18 Quantum results
{
  const s = light("Quantum", "QUANTUM RESULTS", "Always legal, and far more accurate for Anna",
    "A clear win where the answer is clear; no magic on a near-tie. No quantum advantage claimed.",
    `Source: results/canonical/quantum_summary.csv · ideal simulation, ${DATA.quantum.layers} layers, median of 10 runs, 4,096 looks each`);
  const labels = ["Lena", "Thomas", "Anna"], keys = ["growth", "balanced", "risk_sensitive"];
  const series = (metric) => [["Organisers' circuit", "x_penalty"], ["Penalty, tuned", "x_penalty_tuned"], ["Ours", "dicke_xy"]]
    .map(([name, m]) => ({ name, labels, values: keys.map((k) => Q[m][k][metric]) }));
  const common = { barGrouping: "clustered", chartColors: [COL.grey, COL.slate, COL.blue], barGapWidthPct: 50, showValue: true, dataLabelPosition: "outEnd",
    valAxisMinVal: 0, valAxisMaxVal: 1.12, valAxisHidden: true, showTitle: true, titleColor: COL.navy, titleFontSize: 15,
    ...axisStyle({ dataLabelFontSize: 11, valGridLine: { style: "none" } }) };
  s.addChart(pres.charts.BAR, series("legal"), { x: 0.6, y: 1.6, w: 3.75, h: 4.45, ...common, title: "Legal answers", dataLabelFormatCode: "0%", showLegend: true, legendPos: "b", legendFontSize: 11, objectName: "Legal answers chart",
    altText: "Share of legal answers: ours 100% for all savers; organisers' 97 to 98%; tuned penalty 32 to 55%." });
  s.addChart(pres.charts.BAR, series("best"), { x: 4.4, y: 1.6, w: 3.75, h: 4.45, ...common, title: "Chance of naming the best basket", dataLabelFormatCode: "0%", showLegend: true, legendPos: "b", legendFontSize: 11, objectName: "Best basket chart",
    altText: "Chance of naming the best basket: ours 23%, 4%, 78%; organisers' about 5%." });
  const stats = [["100%", "legal answers, every run", COL.blue], [pct(Q.dicke_xy.risk_sensitive.best), "Anna's best basket found (organisers': 5%)", COL.blue],
    [pct(Q.dicke_xy.balanced.best), "for Thomas: no better than guessing", COL.muted]];
  stats.forEach(([big, small, colour], i) => {
    const y = 1.65 + i * 1.47;
    card(s, 8.45, y, 4.25, 1.32);
    text(s, [{ text: big, options: { bold: true, color: colour, fontSize: 34, breakLine: true } }, { text: small, options: { color: COL.body, fontSize: 15 } }],
      8.75, y + 0.12, 3.75, 1.1, { name: "Stat text" });
  });
  s.addNotes("Does it work? Left: every answer from our circuit is a legal basket, in every run. The organisers' circuit is legal ninety-eight percent of the time, " +
    "but then it names Anna's best basket only five percent of the time, which is what blind guessing gives. Ours finds it seventy-eight percent of the time. " +
    "For Thomas, where two baskets are almost equally good, ours is no better than guessing, and we say so. A laptop solves twenty baskets instantly: no quantum advantage.");
}

// 19 Reality check
pres.addSection({ title: "Close" });
{
  const s = light("Close", "REALITY CHECK 2020–2024", "Tech grew more, but losses came more often",
    "Hindsight only: Anna's limit broke for both baskets. Our loss model was too optimistic.",
    "Source: results/canonical (holdout.csv, loss_limits.csv) · Jan 2020–Dec 2024, never used to decide");
  const W = DATA.wealth;
  const years = W.months.map((m) => (m.endsWith("-01") ? m.slice(0, 4) : ""));
  s.addChart(pres.charts.LINE, [{ name: "Today's basket", labels: years, values: W.current }, { name: "Tech basket", labels: years, values: W.proposal }],
    { x: 0.6, y: 1.6, w: 6.0, h: 4.45, chartColors: [COL.blue, COL.tech], lineSize: 2.5, lineDataSymbol: "none", showLegend: true, legendPos: "t",
      catAxisLabelFrequency: 1, catAxisLabelRotate: 0, catAxisMajorTickMark: "none", valAxisMinVal: 0.8, valAxisMaxVal: 2.0, valAxisLabelFormatCode: "0.0", showTitle: true,
      title: `\u20ac1 invested in 2020: \u20ac${W.proposal.at(-1).toFixed(2)} (tech) vs \u20ac${W.current.at(-1).toFixed(2)} (today)`, titleColor: COL.navy, titleFontSize: 15,
      ...axisStyle(), objectName: "Wealth chart", altText: "Wealth 2020 to 2024 after switching cost: tech basket 1.86, today's basket 1.38." });
  const labels = ["Lena (>8%)", "Thomas (>5%)", "Anna (>3%)"], keys = ["growth", "balanced", "risk_sensitive"];
  const real = (role) => keys.map((k) => DATA.loss_months[k][role].at(-1));
  s.addChart([
    { type: pres.charts.BAR, data: [{ name: "Today's basket", labels, values: real("current") }, { name: "Tech basket", labels, values: real("proposal") }],
      options: { barGrouping: "clustered", chartColors: [COL.blue, COL.tech], barGapWidthPct: 60, showValue: true, dataLabelPosition: "outEnd" } },
    { type: pres.charts.LINE, data: [{ name: `Limit: ${DATA.allowed} of 60`, labels, values: labels.map(() => DATA.allowed) }],
      options: { chartColors: [COL.anna], lineSize: 2, lineDash: "dash", lineDataSymbol: "none" } },
  ], { x: 6.8, y: 1.6, w: 5.9, h: 4.45, showLegend: true, legendPos: "t", valAxisMinVal: 0, valAxisMaxVal: 14, showTitle: true,
    title: "Real loss months in 2020–24 (of 60)", titleColor: COL.navy, titleFontSize: 15, ...axisStyle(), objectName: "Real loss months chart",
    altText: "Real loss months 2020 to 2024: Lena 2 and 2, Thomas 5 and 8, Anna 12 and 12; at most 6 allowed." });
  s.addNotes("Finally, a reality check with 2020 to 2024, data we never used to decide. Tech grew to 1.86 against 1.38, so Lena's switch paid off. " +
    "But losses came more often than our model expected: Thomas's tech basket would have broken his limit, and Anna's limit broke for both baskets. " +
    "Our loss model, built on calm years, was too optimistic, and we say that openly.");
}

// 20 Policy
{
  const s = light("Close", "POLICY", "Three rules for using this responsibly", "Policy sets the limits; people make the final call.",
    "Sources: Alterssicherungskommission (June 2026); team policy brief");
  numberedCards(s, [["REVISED", "Protect the default", "Savers choose a profile. Those who don't land in balanced and need protection from fragile bets."],
    ["ADOPTED", "Law sets limits, committee sets the mix", "Limits are checked exactly and never traded for return."],
    ["ADOPTED", "Burden of proof", "Switch only with the same winner in every test and at least 70% support."]]);
  s.addNotes("What should policy do? First, protect the default: people who never choose land in balanced and must be shielded from fragile bets. " +
    "Second, the law sets the limits and the committee sets the mix; limits are checked exactly and never traded for return. " +
    "Third, a burden of proof: switch only when the same basket wins every test with at least seventy percent support.");
}

// 21 Conclusion
{
  const s = dark("Close", "CONCLUSION", "Clear answers, from a circuit that keeps the rules");
  const res = { lena: "SWITCH", thomas: "REVIEW", anna: "KEEP" };
  ["lena", "thomas", "anna"].forEach((who, i) => {
    const x = 0.8 + i * 4.0, sv = SAVER[who];
    portrait(s, who, x, 3.15, 1.3);
    text(s, [{ text: sv.name, options: { color: "E2E8F0", fontSize: 18, breakLine: true } }, { text: res[who], options: { color: sv.colour, fontSize: 34, bold: true } }],
      x + 1.5, 3.2, 2.3, 1.3, { valign: "middle", name: "Verdict" });
  });
  text(s, [{ text: "No quantum advantage, and we say so. One command reproduces every number.", options: { color: COL.sky, fontSize: 20 } }],
    0.8, 5.2, 11.7, 0.6, { name: "Body" });
  s.addNotes("To sum up: Lena switches, Thomas waits for the committee, Anna keeps. Our quantum circuit cannot break the three-sector rule and clearly beats " +
    "the penalty approach where the answer is clear. We claim no quantum advantage, and one command reproduces every number in this talk.");
}

// 22 Thank you
{
  const s = dark("Close", "THANK YOU", "Questions?");
  text(s, [{ text: "Code, decision log and every result: github.com/jonas221101/quantum-hackathon-finance", options: { color: COL.sky, fontSize: 20, breakLine: true } },
    { text: "Ahmed Mahmoud · Ivan · Jonas Sandelmann · Manyu · Mingzhi · Samarth Seth", options: { color: "E2E8F0", fontSize: 16 } }],
  0.8, 3.2, 11.7, 1.2, { name: "Body" });
  s.addNotes("Thank you. We are happy to take questions; the code, the decision log and every result are on GitHub.");
}

(async () => {
  await pres.writeFile({ fileName: OUT });
  // Optional: write the palette into the theme too (PPTX_SKILL_THEME = path to the pptx skill's apply_theme.js).
  // Every colour on the slides is explicit, so the deck looks the same without this step.
  if (process.env.PPTX_SKILL_THEME) await require(process.env.PPTX_SKILL_THEME).applyTheme(OUT, THEME);
  console.log(OUT);
})();
