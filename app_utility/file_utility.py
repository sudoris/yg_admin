# -*- coding: utf-8 -*-
import os
import base64
from io import BytesIO
from datetime import datetime
from app_utility.string_utility import StringUtility


def save_file(upload_file, prefix):
    now = datetime.now()
    original_file_name, file_extension = os.path.splitext(upload_file.filename)
    file_name = prefix + '_' + StringUtility.generate_random_number_and_lowercase_letters(6) + file_extension
    path = os.path.join(os.getcwd(), 'upload_public', str(now.year), str(now.month), file_name)

    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))

    upload_file.save(path)
    return '/{}/{}/{}/{}'.format('upload_public', now.year, now.month, file_name)


def save_base64_str(base64_str, prefix):
    file_extension = '.jpeg'
    if 'image/png' in base64_str.split(',')[0]:
        file_extension = '.png'
    elif 'image/jpg' in base64_str.split(',')[0]:
        file_extension = '.jpg'
    elif 'image/jpeg' in base64_str.split(',')[0]:
        file_extension = '.jpeg'

    now = datetime.now()

    file_name = prefix + '_' + StringUtility.generate_random_number_and_lowercase_letters(6) + file_extension
    path = os.path.join(os.getcwd(), 'upload_public', str(now.year), str(now.month), file_name)

    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))

    base64_str = base64_str.split(',')[1]
    with open(path, "wb") as f:
        f.write(BytesIO(base64.decodebytes(base64_str.encode())).getbuffer().tobytes())

    return '/{}/{}/{}/{}'.format('upload_public', now.year, now.month, file_name)
