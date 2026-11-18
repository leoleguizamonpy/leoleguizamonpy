"""Piezas gráficas del perfil de GitHub de Leo Leguizamón, con diseño editorial: portada, qué hago y cómo trabajo,\ncon la marca personal (símbolo de bloques en ámbar).
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


def mark(x, y, h, color):
    """Logo de Leo: negro sobre fondo claro; en el tema oscuro, invertido para que se vea."""
    k = h / 255.12
    return f'<g transform="translate({x} {y}) scale({k:.4f})">' + "".join(f'<path d="{p}" fill="{color}"/>' for p in MARK) + "</g>"


def neq(x, y, s, color):
    """Signo «distinto de» dibujado (la tipografía en subconjunto latino no lo trae)."""
    return (f'<path d="M{x} {y - s*0.2}H{x+s}M{x} {y + s*0.2}H{x+s}M{x + s*0.7} {y - s*0.55}L{x + s*0.3} {y + s*0.55}" '
            f'fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round"/>')


def frame(W, H, T):
    """Marco de línea fina, como en una pieza impresa."""
    return f'<rect x="24.5" y="24.5" width="{W-49}" height="{H-49}" rx="10" fill="none" stroke="{T["line"]}"/>'


def banner(t):
    """Portada editorial centrada: áreas, marca, nombre, filete ámbar, promesa; lugar y usuario en el pie."""
    T = THEMES[t]; W, H = 1280, 460; cx = W / 2
    b = [f'<rect width="{W}" height="{H}" fill="{T["bg"]}"/>', frame(W, H, T)]
    b.append(text("DISEÑO  ·  ESTRATEGIA  ·  WEB  ·  DOCENCIA", cx, 96, 500, 12, T["quiet"], 0.32, "middle"))
    b.append(mark(cx - 36, 122, 72, T["ink"]))
    size = 84
    total = width("Leo ", 400, size, -0.03) + width("Leguizamón", 700, size, -0.03)
    wm, _ = runs([("Leo ", 400), ("Leguizamón", 700)], cx - total / 2, 286, size, T["ink"], -0.03)
    b.append(wm)
    b.append(f'<rect x="{cx-24}" y="316" width="48" height="2" fill="{AMBER}"/>')
    b.append(text("Diseño marcas con estrategia y las llevo a la web.", cx, 358, 400, 22, T["quiet"], 0, "middle"))
    b.append(text("SAN JUAN BAUTISTA  ·  MISIONES  ·  PARAGUAY", 56, H - 44, 500, 10.5, T["quiet"], 0.28))
    b.append(text("@LEOLEGUIZAMONPY", W - 56, H - 44, 500, 10.5, T["quiet"], 0.28, "end"))
    return svg(W, H, "Leo Leguizamón: diseño marcas con estrategia y las llevo a la web", "".join(b))


SERVICES = [
    ("01", "Identidad de marca", ["Estrategia, logotipo,", "sistema visual y manual."]),
    ("02", "Campañas", ["Concepto y piezas coherentes,", "también institucionales y políticas."]),
    ("03", "Redes sociales", ["Línea gráfica, contenidos", "y calendario."]),
    ("04", "Web y herramientas con IA", ["Sitios a medida y herramientas", "propias para trabajar mejor."]),
]


def services(t):
    """Qué hago: cuatro columnas numeradas, separadas por filetes."""
    T = THEMES[t]; W, H = 1280, 300
    b = [f'<rect width="{W}" height="{H}" fill="{T["bg"]}"/>', frame(W, H, T)]
    b.append(text("QUÉ HAGO", 64, 84, 500, 12, T["quiet"], 0.32))
    col = (W - 128) / 4
    for i, (num, title, lines) in enumerate(SERVICES):
        x = 64 + i * col
        if i:
            b.append(f'<rect x="{x - 20}" y="116" width="1" height="132" fill="{T["line"]}"/>')
        b.append(text(num, x, 136, 600, 13, T["accent"], 0.1))
        b.append(text(title, x, 176, 700, 21, T["ink"], -0.01))
        for j, line in enumerate(lines):
            b.append(text(line, x, 210 + j * 24, 400, 16, T["quiet"]))
    return svg(W, H, "Qué hago: identidad de marca, campañas, redes sociales y web con herramientas de IA", "".join(b))


PRINCIPLES = [
    ("Mide, no promete", ["Cada entrega dice qué está medido", "y qué es una decisión de diseño."]),
    ("Por etapas", ["Avances que se pueden ver, con", "pruebas en cada cambio."]),
    ("Revisado antes de entregar", ["Nada llega al cliente sin pasar", "por una revisión completa."]),
]


def principles(t):
    """Cómo trabajo: la regla de la casa arriba y tres principios."""
    T = THEMES[t]; W, H = 1280, 320
    b = [f'<rect width="{W}" height="{H}" fill="{T["bg"]}"/>', frame(W, H, T)]
    b.append(text("CÓMO TRABAJO", 64, 84, 500, 12, T["quiet"], 0.32))
    x = 64
    for i, (word, w) in enumerate((("Implementado", 400), ("probado", 400), ("validado con casos reales", 700))):
        if i:
            b.append(neq(x + 10, 125, 16, T["ink"]))
            x += 36
        b.append(text(word, x, 134, w, 26, T["ink"], -0.01))
        x += width(word, w, 26, -0.01)
    col = (W - 128) / 3
    for i, (title, lines) in enumerate(PRINCIPLES):
        x = 64 + i * col
        b.append(f'<rect x="{x}" y="176" width="28" height="2" fill="{AMBER}"/>')
        b.append(text(title, x, 214, 700, 19, T["ink"], -0.01))
        for j, line in enumerate(lines):
            b.append(text(line, x, 246 + j * 24, 400, 16, T["quiet"]))
    return svg(W, H, "Cómo trabajo: mide, no promete; por etapas; revisado antes de entregar", "".join(b))


for t in ("light", "dark"):
    open(OUT + f"banner_{t}.svg", "w").write(banner(t))
    open(OUT + f"servicios_{t}.svg", "w").write(services(t))
    open(OUT + f"principios_{t}.svg", "w").write(principles(t))
print("ok")
