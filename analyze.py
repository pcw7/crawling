"""수집한 로또 당첨번호(data/lotto.csv)로 번호별 출현 빈도와 홀짝 비율을 분석한다.

분석 결과는 콘솔에 출력하고, 차트는 output/ 폴더에 PNG로 저장한다.
먼저 collect.py로 데이터를 모아야 한다.
"""
from math import comb
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

BASE_DIR = Path(__file__).parent
DATA_FILE = BASE_DIR / "data" / "lotto.csv"
OUT_DIR = BASE_DIR / "output"
NUM_COLS = ["n1", "n2", "n3", "n4", "n5", "n6"]
NUMBERS = range(1, 46)

# 번호가 완전히 무작위라면 카이제곱 값이 이보다 클 확률은 5%뿐이다. (자유도 44)
CHI2_CRITICAL = 60.48

# 차트 색상
SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_SECONDARY = "#52514e"
INK_MUTED = "#898781"
GRID = "#e1e0d9"
BASELINE = "#c3c2b7"
BLUE = "#2a78d6"
ORANGE = "#eb6834"

plt.rcParams.update({
    "font.family": "Malgun Gothic",  # 윈도우 기본 한글 폰트
    "axes.unicode_minus": False,
    "figure.facecolor": SURFACE,
    "axes.facecolor": SURFACE,
    "axes.edgecolor": BASELINE,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.spines.left": False,
    "axes.grid": True,
    "axes.grid.axis": "y",
    "axes.axisbelow": True,
    "grid.color": GRID,
    "grid.linewidth": 1,
    "axes.titlecolor": INK,
    "axes.titlesize": 14,
    "axes.titleweight": "bold",
    "axes.labelcolor": INK_SECONDARY,
    "xtick.color": INK_MUTED,
    "ytick.color": INK_MUTED,
    "ytick.left": False,
})


# ---------------------------------------------------------------- 분석

def number_frequency(df):
    """1~45 각 번호가 당첨번호(보너스 제외)로 나온 횟수."""
    return df[NUM_COLS].stack().value_counts().reindex(NUMBERS, fill_value=0)


def chi_square(freq):
    """모든 번호가 똑같이 나온다고 가정했을 때와의 차이(카이제곱 통계량)."""
    expected = freq.sum() / len(freq)
    return ((freq - expected) ** 2 / expected).sum()


def odd_even_ratio(df):
    """회차별 홀수 개수(0~6개)의 실제 비율과 이론 확률."""
    odd_count = (df[NUM_COLS] % 2 == 1).sum(axis=1)
    actual = odd_count.value_counts(normalize=True).reindex(range(7), fill_value=0)
    # 1~45에는 홀수 23개, 짝수 22개 → 6개를 뽑을 때 홀수가 k개일 확률(초기하분포)
    theory = pd.Series([comb(23, k) * comb(22, 6 - k) / comb(45, 6) for k in range(7)])
    return actual, theory


def draws_since_last_seen(df):
    """번호별로 마지막으로 나온 뒤 몇 회차째 안 나오고 있는지."""
    long = df.melt(id_vars="draw_no", value_vars=NUM_COLS, value_name="number")
    last_seen = long.groupby("number")["draw_no"].max().reindex(NUMBERS)
    return df["draw_no"].max() - last_seen


def yearly_trend(df):
    """연도별 회당 평균 1등 당첨자 수, 1등 1인당 평균 당첨금, 회당 평균 판매액."""
    df = df.assign(year=df["draw_date"].str[:4].astype(int))
    rows = []
    for year, g in df.groupby("year"):
        won = g[g["first_winners"] > 0]  # 1등이 없어 이월된 회차는 당첨금 평균에서 뺀다
        rows.append({
            "year": int(year),
            "draws": len(g),
            "winners": round(float(g["first_winners"].mean()), 2),
            "prize": int(won["first_prize"].mean()) if len(won) else 0,
            "sales": int(g["total_sales"].mean()),
        })
    return rows


# ---------------------------------------------------------------- 차트

def plot_frequency(freq, draw_range, path):
    expected = freq.sum() / len(freq)
    fig, ax = plt.subplots(figsize=(12, 5), dpi=150)

    ax.bar(freq.index, freq.values, width=0.6, color=BLUE)
    ax.axhline(expected, color=INK_SECONDARY, linewidth=1)
    ax.text(45.6, expected, f"기대값\n{expected:.1f}회", va="center", fontsize=9, color=INK_SECONDARY)

    # 가장 많이/적게 나온 번호에만 값 표시
    for number in [freq.idxmax(), freq.idxmin()]:
        ax.text(number, freq[number] + 2, f"{freq[number]}", ha="center", va="bottom",
                fontsize=9, fontweight="bold", color=INK)

    ax.set_title(f"번호별 당첨 횟수 ({draw_range}, 보너스 제외)", loc="left", pad=12)
    ax.set_xticks(list(NUMBERS))
    ax.tick_params(axis="x", labelsize=8, length=0)
    ax.set_xlim(0.3, 45.7)
    ax.set_ylabel("당첨 횟수")
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def plot_odd_even(actual, theory, draw_range, path):
    x = list(range(7))
    fig, ax = plt.subplots(figsize=(9, 5), dpi=150)

    bars = ax.bar(x, actual * 100, width=0.6, color=BLUE)
    dots, = ax.plot(x, theory * 100, "o", markersize=9, color=ORANGE,
                    markeredgecolor=SURFACE, markeredgewidth=2)

    for k in x:
        top = max(actual[k], theory[k]) * 100
        ax.text(k, top + 1.2, f"{actual[k] * 100:.1f}%", ha="center", va="bottom",
                fontsize=9, color=INK)

    ax.set_title(f"회차별 홀짝 조합 비율 ({draw_range})", loc="left", pad=12)
    ax.set_xticks(x, [f"{k}:{6 - k}" for k in x])
    ax.tick_params(axis="x", labelsize=10, length=0, labelcolor=INK_SECONDARY)
    ax.set_xlabel("홀수 : 짝수")
    ax.set_ylabel("비율 (%)")
    ax.legend([bars, dots], ["실제 비율", "이론 확률"], frameon=False, loc="upper right",
              labelcolor=INK_SECONDARY)
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


# ---------------------------------------------------------------- 실행

def main():
    if not DATA_FILE.exists():
        raise SystemExit("data/lotto.csv가 없습니다. 먼저 collect.py를 실행해 주세요.")

    df = pd.read_csv(DATA_FILE).sort_values("draw_no")
    OUT_DIR.mkdir(exist_ok=True)
    first, last = df.iloc[0], df.iloc[-1]
    draw_range = f"{first.draw_no}~{last.draw_no}회"

    print(f"=== 로또 6/45 분석: {first.draw_no}회({first.draw_date}) ~ "
          f"{last.draw_no}회({last.draw_date}), 총 {len(df)}회 ===\n")

    # 1. 번호별 출현 빈도
    freq = number_frequency(df)
    expected = freq.sum() / len(freq)
    most = freq.sort_values(ascending=False).head(6)
    least = freq.sort_values().head(6)
    chi2 = chi_square(freq)

    print("[1] 번호별 출현 빈도 (보너스 제외)")
    print(f"  기대값: 6개 × {len(df)}회 ÷ 45 = {expected:.1f}회")
    print("  많이 나온 번호: " + ", ".join(f"{n}({c}회)" for n, c in most.items()))
    print("  적게 나온 번호: " + ", ".join(f"{n}({c}회)" for n, c in least.items()))
    verdict = "우연으로 설명되는 수준" if chi2 < CHI2_CRITICAL else "우연이라 보기엔 큰 차이"
    print(f"  카이제곱 {chi2:.1f} (기준 {CHI2_CRITICAL}) → 번호별 차이는 {verdict}\n")

    # 2. 홀짝 비율
    actual, theory = odd_even_ratio(df)
    print("[2] 회차별 홀짝 조합")
    print("  홀:짝    실제    이론")
    for k in range(7):
        print(f"  {k}:{6 - k}   {actual[k] * 100:5.1f}%  {theory[k] * 100:5.1f}%")
    total_odd = (df[NUM_COLS] % 2 == 1).to_numpy().sum()
    print(f"  전체 당첨번호 중 홀수 비율: {total_odd / df[NUM_COLS].size * 100:.1f}% "
          f"(이론 {23 / 45 * 100:.1f}%)\n")

    # 3. 오래 안 나온 번호
    gap = draws_since_last_seen(df).sort_values(ascending=False).head(5)
    print("[3] 오래 안 나온 번호")
    print("  " + ", ".join(f"{n}({g}회째)" for n, g in gap.items()) + "\n")

    plot_frequency(freq, draw_range, OUT_DIR / "number_frequency.png")
    plot_odd_even(actual, theory, draw_range, OUT_DIR / "odd_even.png")
    print(f"차트 저장: {OUT_DIR / 'number_frequency.png'}")
    print(f"           {OUT_DIR / 'odd_even.png'}")


if __name__ == "__main__":
    main()
