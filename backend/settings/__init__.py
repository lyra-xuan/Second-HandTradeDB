import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()


def _get(name, default=None):
    val = os.getenv(name)
    return val if val is not None else default


DB_URI = _get(
    "DB_URI",
    "mysql+aiomysql://root:your_password@127.0.0.1:3306/second_hand_trade?charset=utf8mb4"
)


JWT_SECRET_KEY = _get("JWT_SECRET_KEY", "please_change_this_to_a_random_string")
JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=int(_get("JWT_ACCESS_DAYS", 15)))
