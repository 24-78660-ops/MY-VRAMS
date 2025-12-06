import qrcode
from pathlib import Path
from datetime import datetime

# Create folder for QR codes if it doesn't exist
QR_FOLDER = Path("qr_codes")
QR_FOLDER.mkdir(exist_ok=True)

def generate_sticker_code(user_id: int) -> str:
    # Create a sticker code using last 2 digits of the year + user ID
    year = datetime.now().year % 100
    return f"{year:02d}-{int(user_id):05d}"

def generate_user_qr(user_id, name=None, age=None, address=None, contact=None,
                     department=None, sr_code=None, work_type=None, vehicle_plate=None):
    """
    Generate a QR code that contains only the sticker_code text.
    """
    # Make the sticker code
    sticker_code = generate_sticker_code(user_id)

    # QR will contain only this plain text
    qr_data = sticker_code

    # Create QR object
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4
    )

    # Add data to QR
    qr.add_data(qr_data)
    qr.make(fit=True)

    # Convert QR to an image
    img = qr.make_image(fill_color="black", back_color="white")

    # Save image file
    qr_file = QR_FOLDER / f"{sticker_code}.png"
    img.save(qr_file)

    return sticker_code, str(qr_file)
