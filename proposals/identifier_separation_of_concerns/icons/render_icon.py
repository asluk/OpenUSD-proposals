"""Render SVG icons to transparent PNGs via Edge headless.

Inlines the SVG content into an HTML file with forced scaling,
then screenshots with Edge. Trims and pads the result.
"""
import os
import re
import subprocess
import time
import tempfile
from PIL import Image

EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
ICON_DIR = os.path.dirname(os.path.abspath(__file__))
RENDER_SIZE = 1024
PAD = 60


def render_icon(svg_filename, output_size=RENDER_SIZE):
    svg_path = os.path.join(ICON_DIR, svg_filename)
    png_path = os.path.join(ICON_DIR, svg_filename.replace('.svg', '.png'))

    with open(svg_path, 'r', encoding='utf-8') as f:
        svg_content = f.read()

    svg_content = re.sub(
        r'(<svg[^>]*?)(?:\s+width="[^"]*")?(?:\s+height="[^"]*")?',
        r'\1',
        svg_content,
        count=1
    )
    svg_content = svg_content.replace(
        '<svg ',
        '<svg width="100%" height="100%" ',
        1
    )

    html = f"""<!DOCTYPE html>
<html><head><style>
html, body {{ margin:0; padding:10%; width:80%; height:80%;
             overflow:hidden; background:transparent; }}
</style></head>
<body>{svg_content}</body></html>"""

    html_path = os.path.join(ICON_DIR, '_render_temp.html')
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)

    html_url = 'file:///' + html_path.replace('\\', '/')
    subprocess.run([
        EDGE, '--headless', '--disable-gpu',
        f'--screenshot={png_path}',
        f'--window-size={output_size},{output_size}',
        '--default-background-color=00000000',
        html_url
    ], capture_output=True, timeout=30)
    time.sleep(1)

    img = Image.open(png_path)
    bbox = img.split()[-1].getbbox()
    if bbox:
        cropped = img.crop(bbox)
        final = Image.new('RGBA',
                          (cropped.width + 2 * PAD, cropped.height + 2 * PAD),
                          (0, 0, 0, 0))
        final.paste(cropped, (PAD, PAD))
        final.save(png_path)
        pct = max(cropped.width, cropped.height) / output_size * 100
        print(f'{svg_filename} -> {final.size} ({pct:.0f}% fill)')
    else:
        print(f'{svg_filename} -> EMPTY')

    os.remove(html_path)
    return png_path


if __name__ == '__main__':
    icons = [
        'm48-data-center.svg',
        'm48-robot-manufacturing.svg',
        'm48-workflow.svg',
        'm48-render.svg',
    ]
    for icon in icons:
        render_icon(icon)
