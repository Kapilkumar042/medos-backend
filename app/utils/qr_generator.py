import qrcode
import os


def generate_hospital_qr(
    hospital_code: str
):
    booking_url = (
        f"http://13.200.215.42/book-appointment/{hospital_code}"
    )

    qr = qrcode.QRCode(
        version=1,
        box_size=10,
        border=5
    )

    qr.add_data(booking_url)
    qr.make(fit=True)

    img = qr.make_image(
        fill_color="black",
        back_color="white"
    )

    folder = "uploads/qr"

    os.makedirs(
        folder,
        exist_ok=True
    )

    file_path = (
        f"{folder}/{hospital_code}.png"
    )

    img.save(file_path)

    return file_path
