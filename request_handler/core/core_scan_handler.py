# -*- coding: utf-8 -*-
import qrcode
from io import BytesIO
from barcode import Code128
from barcode.writer import ImageWriter
from flask import Blueprint, send_file


core_scan_handler = Blueprint('core_scan_handler', __name__)


@core_scan_handler.route('/qrcode/<string:qrcode_str>', methods=['GET', 'POST'])
def qrcode_generator(qrcode_str):
    img = qrcode.make(qrcode_str)
    img_io = BytesIO()
    img.save(img_io, 'JPEG', quality=70)
    img_io.seek(0)
    return send_file(img_io, mimetype='image/jpeg')


@core_scan_handler.route('/barcode/<string:barcode_str>', methods=['GET', 'POST'])
def barcode_generator(barcode_str):
    img_io = BytesIO()
    my_code = Code128(barcode_str, writer=ImageWriter())
    my_code.write(img_io, {"module_width":0.35, "module_height":10, "font_size": 18, "text_distance": -3, "quiet_zone": 1, 'write_text': False})
    img_io.seek(0)
    return send_file(img_io, mimetype='image/png')
