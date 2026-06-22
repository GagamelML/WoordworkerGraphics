import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer

# ─── Settings ────────────────────────────────────────────────────────────────
URL         = "https://www.example.com"
OUTPUT_PATH = "qrcode.png"

ERROR_CORRECTION = qrcode.constants.ERROR_CORRECT_H  # L / M / Q / H
BOX_SIZE         = 10    # pixel size of each box
BORDER           = 4     # quiet-zone thickness (in boxes, min. 4)
FILL_COLOR       = "black"
BACK_COLOR       = "white"
ROUNDED_MODULES  = True  # True → rounded dots, False → square dots
# ─────────────────────────────────────────────────────────────────────────────

qr = qrcode.QRCode(
    error_correction=ERROR_CORRECTION,
    box_size=BOX_SIZE,
    border=BORDER,
)
qr.add_data(URL)
qr.make(fit=True)

if ROUNDED_MODULES:
    img = qr.make_image(
        image_factory=StyledPilImage,
        module_drawer=RoundedModuleDrawer(),
        fill_color=FILL_COLOR,
        back_color=BACK_COLOR,
    )
else:
    img = qr.make_image(fill_color=FILL_COLOR, back_color=BACK_COLOR)

img.save(OUTPUT_PATH)
print(f"QR code saved to: {OUTPUT_PATH}")

