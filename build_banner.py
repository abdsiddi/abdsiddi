"""Builds dark.svg and light.svg: an animated terminal-window profile banner.

Reads portrait.txt (see make_portrait.py) for the left panel. Edit INFO below
to change the right panel, then run:  python build_banner.py
"""
from html import escape
from pathlib import Path

W, H = 1200, 620
PORTRAIT_FONT, PORTRAIT_LH = 7.6, 10.6

INFO = [
    ("Subject", "Muhammad Abdullah Siddiqui"),
    ("Role", "SOC Analyst in Training"),
    ("Origin", "Rawalpindi, Pakistan"),
    ("Education", "BSc Cybersecurity, Air University (2027)"),
    ("Status", "Detecting • Hunting • Learning"),
    ("ToolChain", "Splunk, Elastic, Sysmon"),
    None,
    ("Detections", "KQL · MITRE ATT&CK"),
    ("Cloud", "AWS · EC2 · IaC · Honeypots"),
    ("Network", "OSPF · EIGRP · VLAN · Firewalls"),
    None,
    ("Open.To", "SOC & Cloud Security roles"),
    None,
    ("#", "Contact"),
    ("Mail", "muhammad.abdullah.siddiqu@gmail.com"),
    ("GitHub", "github.com/abdsiddi"),
    ("LinkedIn", "in/muhammad-abdullah-siddiqui-1b449a3ab"),
    ("Instagram", "@abdsiwdi"),
]

THEMES = {
    "dark": dict(bg1="#0a0f1e", bg2="#070b16", panel="#0d1526", border="#1f6f8b", accent="#a78bfa",
                 key="#22d3ee", val="#e6edf3", dot="#3b4a63", art="#6f9bff", title="#7d8590",
                 scan="#7dd3fc", grad=("#8b5cf6", "#22d3ee", "#10b981"), live="#f87171"),
    "light": dict(bg1="#f6f8fa", bg2="#eaeef2", panel="#ffffff", border="#0e7490", accent="#6d28d9",
                  key="#0e7490", val="#1f2328", dot="#afb8c1", art="#1e3a8a", title="#57606a",
                  scan="#0ea5e9", grad=("#7c3aed", "#0891b2", "#059669"), live="#dc2626"),
}


def build(name, t):
    art = Path("portrait.txt").read_text(encoding="utf-8").splitlines()
    art_w = max(len(l) for l in art) * PORTRAIT_FONT * 0.6
    art_h = len(art) * PORTRAIT_LH
    ax = 16 + (470 - art_w) / 2
    ay = 84 + (466 - art_h) / 2 + PORTRAIT_LH
    tspans = "\n".join(
        f'<tspan x="{ax:.1f}" y="{ay + i * PORTRAIT_LH:.1f}">{escape(l)}</tspan>' for i, l in enumerate(art)
    )

    rows, y = [], 132
    for item in INFO:
        if item is None:
            y += 12
            continue
        k, v = item
        if k == "#":  # section header, like the top of the panel
            rows.append(
                f'<text x="556" y="{y}" class="mono" font-size="14" font-weight="700" fill="{t["accent"]}">- {escape(v)} '
                f'<tspan fill="{t["dot"]}" font-weight="400">{"─" * 44}</tspan></text>'
            )
            y += 26
            continue
        dots = "." * max(3, 24 - len(k))
        rows.append(
            f'<text x="556" y="{y}" class="mono" font-size="14" xml:space="preserve">'
            f'<tspan fill="{t["dot"]}">. </tspan><tspan fill="{t["key"]}" font-weight="700">{escape(k)}</tspan>'
            f'<tspan fill="{t["dot"]}">: {dots} </tspan><tspan fill="{t["val"]}">{escape(v)}</tspan></text>'
        )
        y += 26
    info = "\n".join(rows)
    g1, g2, g3 = t["grad"]
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Muhammad Abdullah Siddiqui - SOC analyst in training">
<defs>
<linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{t["bg1"]}"/><stop offset="1" stop-color="{t["bg2"]}"/></linearGradient>
<linearGradient id="rim" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{g1}"/><stop offset=".55" stop-color="{g2}"/><stop offset="1" stop-color="{g3}"/></linearGradient>
<linearGradient id="beam" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{t["scan"]}" stop-opacity="0"/><stop offset=".5" stop-color="{t["scan"]}" stop-opacity=".55"/><stop offset="1" stop-color="{t["scan"]}" stop-opacity="0"/></linearGradient>
<clipPath id="win"><rect x="2" y="2" width="{W - 4}" height="{H - 4}" rx="16"/></clipPath>
<style>
.mono{{font-family:'SFMono-Regular',Consolas,'Liberation Mono',Menlo,monospace}}
.blink{{animation:blink 1.1s steps(2,start) infinite}}
@keyframes blink{{to{{visibility:hidden}}}}
</style>
</defs>
<rect x="2" y="2" width="{W - 4}" height="{H - 4}" rx="16" fill="url(#bg)" stroke="url(#rim)" stroke-width="3"/>
<g clip-path="url(#win)">
<rect x="2" y="2" width="{W - 4}" height="44" fill="{t["panel"]}" opacity=".7"/>
<circle cx="26" cy="24" r="6.5" fill="#ff5f57"/><circle cx="46" cy="24" r="6.5" fill="#febc2e"/><circle cx="66" cy="24" r="6.5" fill="#28c840"/>
<text x="{W / 2}" y="29" text-anchor="middle" class="mono" font-size="13" fill="{t["title"]}">abdsiddi@soc ~ % ./profile.sh --live</text>
<circle cx="1052" cy="24" r="5" fill="{t["live"]}"><animate attributeName="opacity" values="1;.25;1" dur="1.6s" repeatCount="indefinite"/></circle>
<text x="1064" y="28" class="mono" font-size="11" fill="{t["live"]}" letter-spacing="1.5">SCANNING</text>

<rect x="14" y="66" width="500" height="522" rx="12" fill="{t["panel"]}" fill-opacity=".55" stroke="{t["border"]}" stroke-opacity=".6"/>
<text x="30" y="60" class="mono" font-size="11" fill="{t["border"]}" letter-spacing="2">VISUAL.MAP</text>
<text class="mono" font-size="{PORTRAIT_FONT}" fill="{t["art"]}" xml:space="preserve">
{tspans}
</text>

<rect x="530" y="66" width="656" height="522" rx="12" fill="{t["panel"]}" fill-opacity=".55" stroke="{t["border"]}" stroke-opacity=".6"/>
<text x="546" y="60" class="mono" font-size="11" fill="{t["border"]}" letter-spacing="2">SYSTEM.INFO</text>
<text x="556" y="104" class="mono" font-size="17" font-weight="700" fill="{t["accent"]}">abdsiddi@soc <tspan fill="{t["dot"]}" font-weight="400">{"─" * 40}</tspan></text>
{info}
<text x="556" y="{y + 12}" class="mono" font-size="14" fill="{t["key"]}">$ <tspan fill="{t["val"]}">tail -f /var/log/alerts</tspan><tspan class="blink" fill="{t["key"]}"> █</tspan></text>

<rect x="2" y="0" width="{W - 4}" height="90" fill="url(#beam)" opacity=".5">
<animateTransform attributeName="transform" type="translate" values="0,20;0,{H - 90};0,20" dur="7s" repeatCount="indefinite"/>
</rect>
</g>
</svg>
'''


for name, theme in THEMES.items():
    Path(f"{name}.svg").write_text(build(name, theme), encoding="utf-8")
    print("wrote", f"{name}.svg")
