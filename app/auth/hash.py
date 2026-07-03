from pwdlib import PasswordHash

password_hash=PasswordHash.recommended()

# pwd_context = CryptContext(
#     schemes=["bcrypt"],
#     deprecated="auto"
# )

def hash_password(password: str):
    return password_hash.hash(password)

def verify_password(
    plain_password,
    hashed_password
)->bool:
    return password_hash.verify(
        plain_password,
        hashed_password
    )