"""Generate the fastfetch-style profile SVG: ASCII bust on the left, boxed info on the right.

Usage (needs ImageMagick):
    curl -sL "https://github.com/itsskiwee.png?size=460" -o /tmp/avatar.png
    python3 scripts/fetch.py /tmp/avatar.png assets/fetch.svg

Edit `sections` below to change the info text.
"""
import subprocess
import sys
from html import escape
from pathlib import Path

AVATAR, OUT = sys.argv[1], Path(sys.argv[2])

FONT = "'JetBrains Mono','Fira Code',ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"
BG = "#0a0a0a"
EDGE = "#1f1f1f"
LINE = "#3a3a3a"
KEY = "#d6d6d6"
VAL = "#8a8a8a"
EMBER = "#e8743b"

W = 860
PAD = 28

# ---------------------------------------------------------------- ascii bust
COLS, ROWS = 72, 43
ACW, ALH, ASIZE = 4.8, 9.6, 8
raw = subprocess.run(["magick", AVATAR, "-colorspace", "Gray", "-crop", "360x420+50+0", "+repage",
                      "-blur", "0x1.5", "-resize", "50%", "-equalize", "-blur", "0x0.8",
                      "-resize", f"{COLS}x{ROWS}!", "-depth", "8", "gray:-"], capture_output=True, check=True).stdout
RAMP = " .:-=+*#%@"
LEVELS = 12


def shade(v):
    # Map brightness to a gray between barely-visible and near-white.
    g = int(0x0a + (0xf0 - 0x0a) * (v / (LEVELS - 1)) ** 0.9)
    return f"#{g:02x}{g:02x}{g:02x}"


# ---------------------------------------------------------------- info column
SIZE, CW, LH = 13, 7.8, 19
BOX = 46  # inner width of the section boxes, in characters
KEYW = 10
sections = [
    ("human", [
        ("name", "ryan rawal"),
        ("role", "cybersecurity student · canada"),
        ("org", "co-founder @ norysr"),
        ("research", "nanomax · eeg, gait"),
        ("building", "platform @ antaraloka"),
        ("focus", "offsec · defsec · opsec"),
        ("learning", "rust · react · ruby · aws"),
    ]),
    ("system", [
        ("os", "omarchy (arch linux)"),
        ("wm", "hyprland (wayland)"),
        ("host", "thinkpad t14 gen 3"),
    ]),
    ("contact", [
        ("site", "norysr.com"),
        ("mail", "ryan.rawal43@gmail.com"),
        ("words", "substack.com/@itsskiweee1"),
    ]),
]


def txt(x, y, s, fill, size=SIZE, cw=CW, extra=""):
    return (f'<text x="{x:.1f}" y="{y:.1f}" fill="{fill}" font-size="{size}" '
            f'textLength="{len(s) * cw:.1f}" lengthAdjust="spacingAndGlyphs" {extra}>{escape(s)}</text>')


def box_top(title):
    left = (BOX - len(title) - 2) // 2
    return "┌" + "─" * left + f" {title} " + "─" * (BOX - left - len(title) - 2) + "┐"


css, body = [], []
PROMPT = [("ryan", EMBER), ("@hephaestus", KEY), (" ~ ", VAL), ("$ ", VAL)]
CMD = "fastfetch"
PROMPT_W = sum(len(s) for s, _ in PROMPT) * CW


def prompt(y, cls):
    x, out = PAD, []
    for s, c in PROMPT:
        out.append(txt(x, y, s, c))
        x += len(s) * CW
    return f'<g class="{cls}">' + "".join(out)


# Prompt typing "fastfetch".
TOP = 40
type_start, type_dur = 0.5, len(CMD) * 0.07
body.append(prompt(TOP, "p0") + txt(PAD + PROMPT_W, TOP, CMD, "#ffffff") +
            f'<g class="cover"><rect x="{PAD + PROMPT_W:.1f}" y="{TOP - 15}" width="{len(CMD) * CW + 4:.1f}" height="20" fill="{BG}"/>'
            f'<rect class="cur" x="{PAD + PROMPT_W:.1f}" y="{TOP - 13}" width="{CW:.1f}" height="17" fill="{KEY}"/></g></g>')
css.append(f".cover{{animation:type {type_dur:.2f}s steps({len(CMD)}) {type_start}s forwards,gone 0s {type_start + type_dur + .2:.2f}s forwards}}"
           f"@keyframes type{{to{{transform:translateX({len(CMD) * CW:.1f}px)}}}}")
out_t = type_start + type_dur + .35

# Art scans in row by row.
ART_TOP = TOP + 34
for r in range(ROWS):
    row = raw[r * COLS:(r + 1) * COLS]
    spans, prev, run = [], None, ""
    for v in row:
        b = (v / 255) ** 0.6
        ch = RAMP[min(len(RAMP) - 1, int(b * len(RAMP)))]
        lvl = min(LEVELS - 1, int(b * LEVELS))
        if lvl != prev and run:
            spans.append(f'<tspan fill="{shade(prev)}">{escape(run)}</tspan>')
            run = ""
        prev, run = lvl, run + ch
    spans.append(f'<tspan fill="{shade(prev)}">{escape(run)}</tspan>')
    y = ART_TOP + r * ALH
    body.append(f'<text class="a" style="animation-delay:{out_t + r * .03:.2f}s" x="{PAD}" y="{y}" font-size="{ASIZE}" '
                f'textLength="{COLS * ACW:.1f}" lengthAdjust="spacingAndGlyphs">{"".join(spans)}</text>')
ART_H = ROWS * ALH

# Info column, appearing line by line beside the art.
IX = PAD + COLS * ACW + 34
y = ART_TOP + 2
k = 0


def info_line(parts):
    global y, k
    x, segs = IX, []
    for s, c in parts:
        segs.append(txt(x, y, s, c))
        x += len(s) * CW
    body.append(f'<g class="a" style="animation-delay:{out_t + .15 + k * .05:.2f}s">' + "".join(segs) + "</g>")
    y += LH
    k += 1


info_line([("ryan", EMBER), ("@", VAL), ("hephaestus", KEY)])
info_line([("─" * len("ryan@hephaestus"), LINE)])
for title, items in sections:
    info_line([(box_top(title), LINE)])
    for i, (key, val) in enumerate(items):
        branch = "└ " if i == len(items) - 1 else "├ "
        info_line([("│ " if i < len(items) - 1 else "└ ", LINE), (branch, LINE), (key.ljust(KEYW), KEY), (val, VAL)])
    info_line([("└" + "─" * BOX + "┘", LINE)])

# Palette row, fastfetch style: grayscale ramp ending in a single ember.
swatches = ["#1a1a1a", "#2e2e2e", "#4a4a4a", "#6b6b6b", "#8f8f8f", "#b5b5b5", "#dcdcdc", EMBER]
sx = IX
blocks = "".join(f'<rect x="{sx + i * 26:.1f}" y="{y - 12}" width="22" height="14" rx="2" fill="{c}"/>' for i, c in enumerate(swatches))
body.append(f'<g class="a" style="animation-delay:{out_t + .15 + k * .05:.2f}s">{blocks}</g>')
y += LH

done = out_t + max(ROWS * .03, .15 + k * .05) + .4
H = int(max(ART_TOP + ART_H, y) + 28 + LH)
end_y = H - 22
body.append(prompt(end_y, "pend") + f'<rect class="cur" x="{PAD + PROMPT_W:.1f}" y="{end_y - 13}" width="{CW:.1f}" height="17" fill="{KEY}"/></g>')
css.append(f".pend{{opacity:0;animation:show .01s {done:.2f}s forwards}}")

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="fastfetch: ryan@hephaestus">
<style>
text{{font-family:{FONT};white-space:pre}}
@keyframes show{{to{{opacity:1}}}}
@keyframes gone{{to{{opacity:0}}}}
@keyframes blink{{50%{{opacity:0}}}}
@keyframes ember{{0%,100%{{opacity:.10}}50%{{opacity:.22}}}}
.cur{{animation:blink 1s step-end infinite}}
.a{{opacity:0;animation-name:show;animation-duration:.25s;animation-fill-mode:forwards}}
.glow{{animation:ember 5s ease-in-out infinite}}
{"".join(css)}
</style>
<defs>
<clipPath id="win"><rect width="{W}" height="{H}" rx="10"/></clipPath>
<radialGradient id="forge" gradientUnits="userSpaceOnUse" cx="{PAD + COLS * ACW / 2:.0f}" cy="{ART_TOP + ART_H:.0f}" r="{COLS * ACW * .55:.0f}"><stop offset="0" stop-color="{EMBER}"/><stop offset="1" stop-color="{EMBER}" stop-opacity="0"/></radialGradient>
</defs>
<g clip-path="url(#win)">
<rect width="{W}" height="{H}" fill="{BG}"/>
<rect class="glow" width="{W}" height="{H}" fill="url(#forge)"/>
{chr(10).join(body)}
</g>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="10" fill="none" stroke="{EDGE}"/>
</svg>
'''
OUT.write_text(svg)
print(OUT, len(svg), "bytes", H, "px tall")
