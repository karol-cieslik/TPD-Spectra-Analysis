"""Render the original Studio vector mark to PNG and Windows multi-size ICO.

Developer-only: Pillow is already a Matplotlib dependency. No downloaded art,
fonts, or runtime image-rendering dependencies are used.
"""
from pathlib import Path
from PIL import Image, ImageDraw

DEST = Path(__file__).resolve().parents[1] / "tpd_spectra" / "assets"
NAVY, MINT = "#142D3B", "#8DE2CF"
SEGMENTS = [
    ((40, 183), (62, 183), (63, 183), (76, 120)),
    ((76, 120), (83, 80), (90, 65), (101, 65)),
    ((101, 65), (119, 65), (110, 183), (133, 183)),
    ((133, 183), (149, 183), (147, 122), (167, 122)),
    ((167, 122), (186, 122), (183, 183), (216, 183)),
]


def render(size):
    scale = size * 4 / 256
    image = Image.new("RGBA", (size * 4, size * 4))
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle(tuple(int(v * scale) for v in (0, 0, 255, 255)),
                           radius=round(52 * scale), fill=NAVY)
    points = []
    for controls in SEGMENTS:
        for step in range(101):
            t = step / 100
            weights = ((1-t)**3, 3*(1-t)**2*t, 3*(1-t)*t*t, t**3)
            points.append(tuple(round(sum(w*p[axis] for w, p in zip(weights, controls)) * scale)
                                for axis in (0, 1)))
    width = max(1, round(15 * scale))
    draw.line(points, fill=MINT, width=width, joint="curve")
    for x, y in (points[0], points[-1]):
        radius = width / 2
        draw.ellipse((x-radius, y-radius, x+radius, y+radius), fill=MINT)
    return image.resize((size, size), Image.Resampling.LANCZOS)


def main():
    DEST.mkdir(parents=True, exist_ok=True)
    path = "M40 183 " + " ".join("C" + " ".join(f"{x} {y}" for x, y in segment[1:]) for segment in SEGMENTS)
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" role="img" aria-labelledby="title">\n'
           '<title id="title">TPD Spectra Studio — spectrum mark</title>\n'
           f'<rect width="256" height="256" rx="52" fill="{NAVY}"/>\n'
           f'<path d="{path}" fill="none" stroke="{MINT}" stroke-width="15" stroke-linecap="round" stroke-linejoin="round"/>\n</svg>\n')
    (DEST / "studio-mark.svg").write_text(svg, encoding="utf-8")
    for size in (16, 32, 48, 64, 128, 256):
        render(size).save(DEST / f"studio-{size}.png")
    render(256).save(DEST / "studio.ico", sizes=[(s, s) for s in (16, 20, 24, 32, 40, 48, 64, 128, 256)])


if __name__ == "__main__":
    main()
