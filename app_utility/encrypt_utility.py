# -*- coding: utf-8 -*-
import base64
import bcrypt
import hashlib


class BcryptUtility:

    @staticmethod
    def hash_password(password: str):
        """ 回傳長度為60加密過的密碼"""
        mix_password = base64.b64encode(hashlib.sha256(password.encode('utf-8')).digest())
        return bcrypt.hashpw(mix_password, bcrypt.gensalt(15))

    @staticmethod
    def verify_password(original_password, encrypted_password):
        """
        檢查密碼
        :param original_password 未加密過的密碼
        :param encrypted_password 加密過的密碼
        :return 密碼是否正確
        """
        mix_password = base64.b64encode(hashlib.sha256(original_password.encode('utf-8')).digest())
        return bcrypt.checkpw(mix_password, encrypted_password.encode('utf-8'))
