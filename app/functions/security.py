import hashlib

def hash_password(password: str) -> str:
    weekly_prefix = "sloopy_summer_"
    pwd = weekly_prefix + password
    return hashlib.sha256(pwd.encode('utf-8')).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return hash_password(plain_password) == hashed_password