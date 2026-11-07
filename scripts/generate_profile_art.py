"""Piezas gráficas del perfil de GitHub de Leo Leguizamón: banner con la marca personal (símbolo de bloques en ámbar).
Textos convertidos a trazos con Inter Tight (HarfBuzz) para que GitHub los muestre igual en todos lados.
Uso: pip install fonttools brotli uharfbuzz && python scripts/generate_profile_art.py"""
import io, sys
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
import uharfbuzz as hb

import os
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FONTDIR = os.path.join(ROOT, "scripts/fonts") + "/"
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "img") + "/"
_F = {}


def font(w):
    if w not in _F:
        tt = TTFont(FONTDIR + f"inter-tight-latin-{w}-normal.woff2")
        tt.flavor = None
        buf = io.BytesIO(); tt.save(buf); data = buf.getvalue()
        face = hb.Face(data); hf = hb.Font(face)
        _F[w] = (tt, hf, tt["head"].unitsPerEm)
    return _F[w]


def shape(txt, w, size, track=0.0):
    tt, hf, upem = font(w)
    b = hb.Buffer(); b.add_str(txt); b.guess_segment_properties()
    hb.shape(hf, b, {"kern": True, "liga": True})
    order = tt.getGlyphOrder()
    s = size / upem
    out, x = [], 0.0
    for info, pos in zip(b.glyph_infos, b.glyph_positions):
        out.append((order[info.codepoint], x + pos.x_offset * s))
        x += pos.x_advance * s + track * size
    return out, x - track * size


def width(txt, w, size, track=0.0):
    return shape(txt, w, size, track)[1]


def text(txt, x, y, w, size, fill, track=0.0, anchor="start"):
    tt, _, upem = font(w)
    glyphs, total = shape(txt, w, size, track)
    if anchor == "end": x -= total
    elif anchor == "middle": x -= total / 2
    gs = tt.getGlyphSet(); s = size / upem
    d = []
    for name, gx in glyphs:
        pen = SVGPathPen(gs, ntos=lambda v: ('%.1f' % v).rstrip('0').rstrip('.'))
        gs[name].draw(TransformPen(pen, (s, 0, 0, -s, x + gx, y)))
        if pen.getCommands(): d.append(pen.getCommands())
    return f'<path fill="{fill}" d="{" ".join(d)}"/>'


def runs(parts, x, y, size, fill, track=0.0):
    """parts = [(texto, peso), ...] en una misma línea."""
    out = []
    for t, w in parts:
        out.append(text(t, x, y, w, size, fill, track)); x += width(t, w, size, track)
    return "".join(out), x


def arrow(x, y, w, color, sw=2):
    return (f'<path d="M{x} {y}H{x+w}M{x+w-5} {y-5}L{x+w} {y}L{x+w-5} {y+5}" fill="none" stroke="{color}" '
            f'stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round"/>')


def check(x, y, s, color, sw=2.2):
    return f'<path d="M{x} {y+s*0.5}L{x+s*0.38} {y+s*0.85}L{x+s} {y+s*0.1}" fill="none" stroke="{color}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round"/>'


def cross(x, y, s, color, sw=2.2):
    return f'<path d="M{x} {y}L{x+s} {y+s}M{x+s} {y}L{x} {y+s}" fill="none" stroke="{color}" stroke-width="{sw}" stroke-linecap="round"/>'


def svg(w, h, label, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="{label}">'
            f'{body}</svg>\n')






# Marca personal: dos bloques que se encastran (viewBox 267.41 × 255.12).
MARK = ["M123.27 0V117.97H113.75V255.12H0V0Z", "M267.41 0V255.12H144.14V137.15H153.63V0Z"]
AMBER = "#F8A913"
THEMES = {
    "light": dict(bg="#F4F3EF", card="#FFFFFF", line="#E2E0D9", ink="#17191E", quiet="#5A5852", accent="#8F5A00"),
    "dark": dict(bg="#0F1013", card="#17191E", line="#2B2D33", ink="#F2F2F0", quiet="#A9ABB2", accent=AMBER),
}


def mark(x, y, h):
    k = h / 255.12
    return f'<g transform="translate({x} {y}) scale({k:.4f})">' + "".join(f'<path d="{p}" fill="{AMBER}"/>' for p in MARK) + "</g>"


def banner(t):
    """Solo la columna izquierda: lugar, marca, nombre, promesa y áreas de trabajo."""
    T = THEMES[t]; W, H = 1280, 400
    b = [f'<rect width="{W}" height="{H}" fill="{T["bg"]}"/>']
    b.append(f'<rect x="24.5" y="24.5" width="{W-49}" height="{H-49}" rx="28" fill="{T["card"]}" stroke="{T["line"]}"/>')
    b.append(text("SAN JUAN BAUTISTA  ·  MISIONES  ·  PARAGUAY", 88, 100, 600, 14, T["accent"], 0.12))
    b.append(mark(90, 128, 70))
    wm, _ = runs([("Leo ", 400), ("Leguizamón", 700)], 86, 264, 66, T["ink"], -0.025)
    b.append(wm)
    b.append(text("Diseño marcas con estrategia y las llevo a la web.", 88, 308, 500, 24, T["ink"], -0.01))
    x = 88
    for i, item in enumerate(("Diseño gráfico", "Estrategia de marca", "Docencia", "Desarrollo fullstack con IA")):
        if i:
            b.append(f'<rect x="{x}" y="331" width="1" height="20" fill="{T["line"]}"/>')
            x += 18
        b.append(text(item, x, 346, 400, 16, T["quiet"]))
        x += width(item, 400, 16) + 18
    return svg(W, H, "Leo Leguizamón: diseño marcas con estrategia y las llevo a la web", "".join(b))


for t in ("light", "dark"):
    open(OUT + f"banner_{t}.svg", "w").write(banner(t))
print("ok")
