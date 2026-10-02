"""수집 데이터(data/lotto.csv)를 암호화해서 레포에 보관하기 위한 도구.

GitHub Actions 서버(해외 IP)는 동행복권에 몇 번밖에 접속할 수 없어서 매주 새 회차만 받아야 한다.
그러려면 이전 데이터가 필요하지만 원본 데이터는 공개하지 않기로 했으므로,
암호화한 파일(lotto.csv.enc)만 레포에 올리고 키는 GitHub Secrets(LOTTO_DATA_KEY)에 둔다.

사용법 (키는 환경 변수 LOTTO_DATA_KEY에서 읽는다):
    python data_crypt.py encrypt   # data/lotto.csv → lotto.csv.enc
    python data_crypt.py decrypt   # lotto.csv.enc → data/lotto.csv
"""
import gzip
import os
import sys
from pathlib import Path

from cryptography.fernet import Fernet

from collect import DATA_FILE

ENC_FILE = Path(__file__).parent / "lotto.csv.enc"


def get_cipher():
    key = os.environ.get("LOTTO_DATA_KEY")
    if not key:
        sys.exit("환경 변수 LOTTO_DATA_KEY가 없습니다.")
    return Fernet(key)


def encrypt():
    ENC_FILE.write_bytes(get_cipher().encrypt(gzip.compress(DATA_FILE.read_bytes())))
    print(f"암호화: {DATA_FILE} → {ENC_FILE}")


def decrypt():
    DATA_FILE.parent.mkdir(exist_ok=True)
    DATA_FILE.write_bytes(gzip.decompress(get_cipher().decrypt(ENC_FILE.read_bytes())))
    print(f"복호화: {ENC_FILE} → {DATA_FILE}")


if __name__ == "__main__":
    commands = {"encrypt": encrypt, "decrypt": decrypt}
    if len(sys.argv) != 2 or sys.argv[1] not in commands:
        sys.exit("사용법: python data_crypt.py encrypt | decrypt")
    commands[sys.argv[1]]()
