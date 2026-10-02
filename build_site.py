"""분석 결과를 GitHub Pages용 웹페이지로 만든다.

data/lotto.csv를 기간별(전체, 최근 100회, 최근 50회)로 집계해서
site_template.html의 __DATA__ 자리에 JSON으로 넣고, GitHub Pages가 보여주는 docs/index.html로 저장한다.
원본 당첨번호 전체는 넣지 않고 집계 결과만 넣는다.
"""
import json
from pathlib import Path

import pandas as pd

from analyze import (CHI2_CRITICAL, DATA_FILE, NUM_COLS, chi_square,
                     draws_since_last_seen, number_frequency, odd_even_ratio)

BASE_DIR = Path(__file__).parent
TEMPLATE_FILE = BASE_DIR / "site_template.html"
OUT_FILE = BASE_DIR / "docs" / "index.html"
WINDOWS = {"all": None, "100": 100, "50": 50}  # 최근 N회 (None은 전체)


def summarize(df):
    """한 기간의 번호별 빈도, 홀짝 비율, 카이제곱 값."""
    freq = number_frequency(df)
    actual, _ = odd_even_ratio(df)
    return {
        "draws": len(df),
        "freq": freq.tolist(),
        "oddEven": [round(x, 4) for x in actual],
        "chi2": round(float(chi_square(freq)), 1),
    }


def main():
    if not DATA_FILE.exists():
        raise SystemExit("data/lotto.csv가 없습니다. 먼저 collect.py를 실행해 주세요.")

    df = pd.read_csv(DATA_FILE).sort_values("draw_no")
    first, last = df.iloc[0], df.iloc[-1]
    _, theory = odd_even_ratio(df)

    # 같은 데이터면 항상 같은 페이지가 나오도록 생성 날짜 같은 값은 넣지 않는다.
    # (자동 갱신 때 새 회차가 없으면 바뀐 게 없어 커밋하지 않게 하려는 것)
    data = {
        "first": {"no": int(first.draw_no), "date": first.draw_date},
        "last": {
            "no": int(last.draw_no),
            "date": last.draw_date,
            "numbers": [int(last[col]) for col in NUM_COLS],
            "bonus": int(last.bonus),
        },
        "chi2Critical": CHI2_CRITICAL,
        "oddEvenTheory": [round(x, 4) for x in theory],
        "gap": draws_since_last_seen(df).astype(int).tolist(),
        "windows": {key: summarize(df if n is None else df.tail(n)) for key, n in WINDOWS.items()},
    }

    html = TEMPLATE_FILE.read_text(encoding="utf-8")
    html = html.replace("__DATA__", json.dumps(data, ensure_ascii=False))
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUT_FILE.write_text(html, encoding="utf-8")
    print(f"웹페이지 생성: {OUT_FILE} ({last.draw_no}회 기준)")


if __name__ == "__main__":
    main()
