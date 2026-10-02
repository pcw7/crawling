# 로또 6/45 당첨번호 분석

동행복권 사이트에서 1회차부터 최신 회차까지 당첨번호를 수집하고,
번호별 출현 빈도와 홀짝 비율을 분석합니다.

**웹페이지: https://pcw7.github.io/crawling/lotto/**

## 실행

```bash
pip install -r requirements.txt
python collect.py      # 당첨번호 수집 → data/lotto.csv
python analyze.py      # 분석 결과 출력 + 차트 → output/
python build_site.py   # 웹페이지 생성 → ../docs/lotto/index.html
```

`collect.py`는 이미 저장된 회차를 건너뛰고 새 회차만 받아 옵니다.

## 자동 갱신

GitHub Actions([`.github/workflows/update-lotto.yml`](../.github/workflows/update-lotto.yml))가 매주 일요일 09:17(한국 시간)에
수집과 페이지 생성을 실행하고, 새 회차가 있으면 커밋·푸시해서 웹페이지를 갱신합니다.
레포의 **Actions 탭 → 로또 통계 갱신 → Run workflow**로 바로 실행할 수도 있습니다.

아래 차트 이미지는 자동 갱신되지 않는 1243회 기준 스냅샷입니다. 최신 결과는 웹페이지에서 볼 수 있습니다.

## 결과 (1~1243회 기준)

![번호별 당첨 횟수](output/number_frequency.png)

- 가장 많이 나온 번호는 34번(186회), 가장 적게 나온 번호는 9번(137회)입니다. 기대값은 165.7회입니다.
- 카이제곱 값은 29.3으로 기준값 60.48(자유도 44, 유의수준 5%)보다 작습니다. 번호별 차이는 우연으로 설명되는 수준입니다.

![회차별 홀짝 조합 비율](output/odd_even.png)

- 가장 흔한 조합은 홀짝 3:3(33.3%)이며, 각 조합의 비율이 이론 확률(초기하분포)과 거의 같습니다.

## 파일

| 파일 | 내용 |
|---|---|
| `collect.py` | 동행복권에서 당첨번호를 수집해 CSV로 저장 |
| `analyze.py` | 번호별 빈도, 홀짝 비율, 오래 안 나온 번호 분석 및 차트 생성 |
| `build_site.py` | 기간별(전체, 최근 100회, 최근 50회) 집계 결과를 `site_template.html`에 넣어 웹페이지 생성. 원본 데이터는 넣지 않습니다 |
| `site_template.html` | 웹페이지 틀 (HTML, CSS, 자바스크립트 차트) |
| `data/lotto.csv` | 수집한 데이터 (회차, 추첨일, 번호 6개, 보너스, 1등 당첨자 수·당첨금, 총판매금액). 레포에는 포함하지 않으며 `collect.py`를 실행하면 생성됩니다 |
| `output/*.png` | 분석 차트 |

## 데이터 출처

동행복권 당첨결과 페이지(`/lt645/result`)가 화면을 그릴 때 내부적으로 호출하는
JSON 주소(`/lt645/selectPstLt645InfoNew.do`)를 사용합니다.

- robots.txt에서 차단하는 경로는 `/resources/`, `/winImages/`뿐입니다. (2026-10-02 확인)
- 서버 부담을 줄이려고 요청 사이에 1초씩 쉽니다.
- 사이트가 개편되면 주소나 응답 형식이 바뀔 수 있습니다.
