import hashlib
import hmac
import os


class AuthService:
    iterations = 120_000

    def hash_password(self, password: str) -> str:
        salt = os.urandom(16)
        digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, self.iterations)
        return f"{salt.hex()}:{digest.hex()}"

    def verify_password(self, password: str, stored_hash: str) -> bool:
        try:
            salt_hex, digest_hex = stored_hash.split(":", maxsplit=1)
        except ValueError:
            return False

        salt = bytes.fromhex(salt_hex)
        expected = bytes.fromhex(digest_hex)
        actual = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, self.iterations)
        return hmac.compare_digest(actual, expected)
