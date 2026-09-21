#!/usr/bin/env node
/**
 * Draws an animated "jet over the contribution grid" SVG from your real
 * GitHub contribution calendar (last 34 weeks x 7 days).
 *
 * The jet sweeps the grid and fires at your busiest days, which flash green.
 *
 * Env:
 *   GH_USERNAME  GitHub login (required)
 *   GH_TOKEN     token for the GraphQL API; the Actions GITHUB_TOKEN works
 *   OUTPUT_PATH  output file (default dist/github-jet.svg)
 *   MOCK=1       skip the API and draw an empty grid (local preview only)
 */
import fs from "node:fs";
import path from "node:path";

const USER = process.env.GH_USERNAME;
const TOKEN = process.env.GH_TOKEN || process.env.GITHUB_TOKEN;
const OUT = process.env.OUTPUT_PATH || "dist/github-jet.svg";
const MOCK = process.env.MOCK === "1";

const COLS = 34, ROWS = 7, CELL = 11, STEP = 14;
const GX = 20, GY = 15, W = 513, H = 170;
const JET_FROM = 35, JET_TO = 478, JET_Y = 140, LOOP = 20, TARGETS = 12;
const EMPTY = "#161b22", FLASH = "#39d353", BULLET = "#7ee787", BLAST = "#56d364";

const QUERY = `query($login:String!){user(login:$login){contributionsCollection{contributionCalendar{weeks{contributionDays{date contributionCount color}}}}}}`;

async function fetchWeeks() {
  if (MOCK) return [];
  if (!USER || !TOKEN) throw new Error("GH_USERNAME and GH_TOKEN are required");
  const res = await fetch("https://api.github.com/graphql", {
    method: "POST",
    headers: { Authorization: `bearer ${TOKEN}`, "Content-Type": "application/json" },
    body: JSON.stringify({ query: QUERY, variables: { login: USER } }),
  });
  if (!res.ok) throw new Error(`GitHub API ${res.status}: ${await res.text()}`);
  const json = await res.json();
  if (json.errors) throw new Error(JSON.stringify(json.errors));
  return json.data.user.contributionsCollection.contributionCalendar.weeks;
}

const n = (v) => Number(v.toFixed(4));

// the last COLS weeks, left-padded with empty weeks for young accounts
function toCells(weeks) {
  const recent = weeks.slice(-COLS);
  const blank = { contributionDays: Array.from({ length: ROWS }, () => ({ contributionCount: 0, color: EMPTY })) };
  const padded = [...Array(COLS - recent.length).fill(blank), ...recent];
  return padded.flatMap((week, col) =>
    Array.from({ length: ROWS }, (_, row) => {
      const d = week.contributionDays[row] ?? { contributionCount: 0, color: EMPTY };
      return { col, row, x: GX + col * STEP, y: GY + row * STEP, color: d.color || EMPTY, count: d.contributionCount };
    })
  );
}

// where the jet is, as a 0..1 fraction of the loop, when it passes a column
const passAt = (col, dir) => {
  const t = 0.02 + (col / (COLS - 1)) * 0.46;
  return dir === "fwd" ? t : 1 - t;
};

function render(cells) {
  const targets = cells.filter((c) => c.count > 0).sort((a, b) => b.count - a.count).slice(0, TARGETS);
  const isTarget = new Set(targets.map((c) => `${c.col}-${c.row}`));
  const blip = 0.006;
  let grid = "", shots = "", blasts = "";

  for (const c of cells) {
    const rect = `x="${c.x}" y="${c.y}" width="${CELL}" height="${CELL}" rx="2" fill="${c.color}"`;
    if (!isTarget.has(`${c.col}-${c.row}`)) { grid += `<rect ${rect}/>\n`; continue; }
    const [a, b] = [passAt(c.col, "fwd"), passAt(c.col, "back")];
    grid += `<rect ${rect}><animate attributeName="fill" dur="${LOOP}s" repeatCount="indefinite" ` +
      `keyTimes="0;${n(a)};${n(a + blip)};${n(b)};${n(b + blip)};1" ` +
      `values="${c.color};${c.color};${FLASH};${c.color};${FLASH};${c.color}"/></rect>\n`;
  }

  for (const dir of ["fwd", "back"]) {
    for (const c of targets) {
      const t = passAt(c.col, dir);
      const cx = c.x + CELL / 2, cy = c.y + CELL / 2, launch = JET_Y - 12;
      shots += `<circle cx="${cx}" cy="${launch}" r="2.4" fill="${BULLET}" opacity="0">` +
        `<animate attributeName="cy" dur="${LOOP}s" repeatCount="indefinite" keyTimes="0;${n(t - blip * 3)};${n(t)};1" values="${launch};${launch};${cy};${cy}"/>` +
        `<animate attributeName="opacity" dur="${LOOP}s" repeatCount="indefinite" keyTimes="0;${n(t - blip * 3)};${n(t)};${n(t + blip)};1" values="0;1;1;0;0"/></circle>\n`;
      blasts += `<circle cx="${cx}" cy="${cy}" r="0" fill="none" stroke="${BLAST}" stroke-width="1.6" opacity="0">` +
        `<animate attributeName="r" dur="${LOOP}s" repeatCount="indefinite" keyTimes="0;${n(t)};${n(t + blip * 3)};1" values="0;1;9;9"/>` +
        `<animate attributeName="opacity" dur="${LOOP}s" repeatCount="indefinite" keyTimes="0;${n(t)};${n(t + blip * 3)};1" values="0;1;1;0"/></circle>\n`;
    }
  }

  const stars = [[8, 20, 1.2], [8, 60, 1.6], [8, 100, 2], [505, 25, 1.2], [505, 70, 1.6], [505, 110, 2], [30, 164, 1.2], [483, 164, 1.6]]
    .map(([x, y, d]) => `<circle cx="${x}" cy="${y}" r="1.1" fill="#8b949e"><animate attributeName="opacity" values="0.2;1;0.2" dur="${d}s" repeatCount="indefinite"/></circle>`)
    .join("\n");

  const jet = `<g><g>
<polygon points="0,-16 8,6 4,3 -4,3 -8,6" fill="#58a6ff" stroke="#1f6feb" stroke-width="1"/>
<polygon points="-8,6 -14,12 -4,7" fill="#388bfd"/><polygon points="8,6 14,12 4,7" fill="#388bfd"/>
<circle cx="0" cy="-6" r="2.2" fill="#c9e6ff"/>
<polygon points="-3,7 3,7 0,15" fill="#f0883e"><animate attributeName="opacity" values="0.5;1;0.6;1" dur="0.18s" repeatCount="indefinite"/></polygon>
</g><animateTransform attributeName="transform" type="translate" dur="${LOOP}s" repeatCount="indefinite" keyTimes="0;0.5;1" values="${JET_FROM},${JET_Y};${JET_TO},${JET_Y};${JET_FROM},${JET_Y}"/></g>`;

  return `<svg viewBox="0 0 ${W} ${H}" xmlns="http://www.w3.org/2000/svg">
<rect width="${W}" height="${H}" fill="#0d1117"/>
${stars}
<g>
${grid}</g>
<g>
${shots}</g>
<g>
${blasts}</g>
${jet}
</svg>
`;
}

const svg = render(toCells(await fetchWeeks()));
fs.mkdirSync(path.dirname(path.resolve(OUT)), { recursive: true });
fs.writeFileSync(OUT, svg, "utf8");
console.log(`wrote ${OUT}${MOCK ? " (mock: empty grid)" : ""}`);
