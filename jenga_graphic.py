from openpyxl import load_workbook
import math
import svgwrite
from svgwrite.container import Group
from svgwrite.path import Path
import xml.etree.ElementTree as ET

# ----------------------
# Parameters

in_file = "C:\\Users\\lohoff\\Documents\\Private\\Makerspace\\Jenga\\Spicy_Jenga_Vorschläge.xlsx"
out_file = "C:\\Users\\lohoff\\Documents\\Private\\Makerspace\\Jenga\\grid.svg"

stone_width = 7.5
stone_height = 2.5

text_height = 1.8
text_width = 5.5
font_size = 0.8

icon_size = 0.8   # cm
icon_gap = 0.3    # cm

width_total = 60

icons = {
    "FF00FF00": "icons/checkmark.svg",
    "FFFF0000": "icons/warning.svg",
}

# -----------------------

assert stone_width > text_width + icon_size + icon_gap, "Text plus icon would be too wide for the block size"

# Load the sheet
wb = load_workbook(in_file, data_only=True)
ws = wb.active  # use first sheet, or wb["SheetName"]

# Get row texts and colors
snippets = []
for row in ws.iter_rows(values_only=False):  # values_only=False so we also get style
    for cell in row:
        if cell.value and isinstance(cell.value, str):
            # Get the text
            text = cell.value.strip()

            # Get the fill color (RGB hex like "FF00FF00" for green)
            fill = cell.fill.fgColor.rgb if cell.fill and cell.fill.fgColor else None

            snippets.append({
                "text": text,
                "color": fill
            })

# Grid calculations
N = int(width_total // stone_width)
M = math.ceil(len(snippets) / N)
grid_width = N * stone_width
grid_height = M * stone_height

dwg = svgwrite.Drawing(out_file, size=(f"{grid_width}cm", f"{grid_height}cm"))

# Draw grid lines
for i in range(N + 1):
    x = i * stone_width
    dwg.add(dwg.line((f"{x}cm", "0cm"), (f"{x}cm", f"{grid_height}cm"),
                     stroke="black", stroke_width=0.1))

for j in range(M + 1):
    y = j * stone_height
    dwg.add(dwg.line(("0cm", f"{y}cm"), (f"{grid_width}cm", f"{y}cm"),
                     stroke="black", stroke_width=0.1))


def wrap_text_to_box(text, font_size, box_width, box_height):
    """
    Wrap text word by word into lines that fit within box_width.
    If text doesn't fit into box_height with current font_size, return None.
    """
    words = text.split()
    lines, current = [], ""

    for word in words:
        test_line = (current + " " + word).strip()
        est_width = 0.6 * font_size * len(test_line)
        if est_width <= box_width:
            current = test_line
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)

    total_height = len(lines) * font_size
    if total_height > box_height:
        return None  # doesn’t fit
    return lines


def load_icon_as_path(filename, max_size):
    """Load an SVG file, extract first path, and scale to fit max_size."""
    tree = ET.parse(filename)
    root = tree.getroot()

    # assume namespace
    ns = {"svg": "http://www.w3.org/2000/svg"}
    path_elem = root.find(".//svg:path", ns)
    if path_elem is None:
        raise ValueError(f"No path found in {filename}")

    d = path_elem.attrib["d"]
    path = Path(d=d, fill="black")

    # naive bounding box scaling (min_x, max_x, min_y, max_y)
    bbox = path.bbox()
    scale = min(max_size / (bbox[2] - bbox[0]), max_size / (bbox[3] - bbox[1]))

    g = Group()
    g.add(path)
    g.scale(scale)
    return g


# --- Place text snippets ---
for idx, item in enumerate(snippets):
    text = item["text"]
    color = item["color"]

    row = idx // N
    col = idx % N

    # Stone top-left corner
    x0 = col * stone_width
    y0 = row * stone_height
    cx = x0 + stone_width / 2
    cy = y0 + stone_height / 2

    # Start with default size
    this_font_size = font_size
    lines = wrap_text_to_box(text, this_font_size, text_width, text_height)

    # Shrink font until text fits
    while lines is None and this_font_size > 0.2:
        this_font_size *= 0.9
        lines = wrap_text_to_box(text, this_font_size, text_width, text_height)

    # Save chosen font size
    item["font_size"] = this_font_size

    if not lines:
        lines = [text]  # fallback, single line

    # --- Icon handling ---
    icon_group = None
    if color and color in icons:
        icon_group = load_icon_as_path(icons[color], icon_size)

    # Measure text block
    text_block_width = max(0.6 * this_font_size * len(line) for line in lines)
    text_block_height = len(lines) * this_font_size

    # If icon present, adjust alignment
    if icon_group:
        total_width = text_block_width + icon_gap + icon_size
    else:
        total_width = text_block_width

    # Compute start X for centering combined block
    block_center_x = cx
    start_x = block_center_x - total_width / 2

    # --- Draw text lines ---
    start_y = cy - text_block_height / 2 + this_font_size / 2
    for i, line in enumerate(lines):
        y = start_y + i * this_font_size
        dwg.add(dwg.text(
            line,
            insert=(f"{start_x + text_block_width / 2}cm", f"{y}cm"),
            text_anchor="middle",
            dominant_baseline="middle",
            font_size=f"{this_font_size}cm",
            font_family="Arial"
        ))

    # --- Place icon if needed ---
    if icon_group:
        icon_x = start_x + text_block_width + icon_gap
        icon_y = cy - icon_size / 2
        icon_group.translate(icon_x, icon_y)
        dwg.add(icon_group)

dwg.save(out_file)


