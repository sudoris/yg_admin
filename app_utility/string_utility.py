# -*- coding: utf-8 -*-
import re
import uuid
import string
import random
import hashlib
import itertools
import unicodedata


class StringUtility:

    @staticmethod
    def verify_mobile(mobile):
        """ 驗證 Mobile """
        if not mobile:
            return False

        if not re.search('^09[0-9]{8}$', mobile):
            return False

        return True

    @staticmethod
    def generate_random_number(length=1):
        """
        產生亂數 數字
        :param length: 字串長度
        :return: 亂數 數字 字串
        """
        chars = string.digits
        return ''.join(random.choice(chars) for _ in range(length))


    @staticmethod
    def generate_random_number_and_lowercase_letters(length=1):
        """
        產生亂數 小寫 英文字母 與數字
        :param length: 字串長度
        :return: 亂數 小寫 英文字母 與數字 字串
        """
        chars = string.digits + string.ascii_lowercase
        return ''.join(random.choice(chars) for _ in range(length))
