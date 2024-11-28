# -*- coding: utf-8 -*-
import os

secret_key = os.environ.get("secret_key")

# Database 連線資訊
db_account = os.environ.get("db_account")
db_password = os.environ.get("db_password")
db_host = os.environ.get("db_host")
db_database = os.environ.get("db_database")


database_url = 'mysql://' + db_account + ':' + db_password + '@' + db_host + '/' + db_database + '?charset=utf8mb4'


key_cbc = os.environ.get("key_cbc")
domain = os.environ.get("domain")

athena_api_url = os.environ.get("athena_api_url") # 德安API

# Member
member_liff_id = os.environ.get("member_liff_id")
member_liff_channel_id = os.environ.get("member_liff_channel_id")
member_line_channel_secret = os.environ.get("member_line_channel_secret")
member_line_channel_access_token = os.environ.get("member_line_channel_access_token")

# User
user_line_channel_secret = os.environ.get("user_line_channel_secret")
user_line_channel_access_token = os.environ.get("user_line_channel_access_token")

# 簡訊
sms_uid = os.environ.get("sms_uid")
sms_pwd = os.environ.get("sms_pwd")
