import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# =============================
# 0. 메타데이터 (고정값)
# =============================
MEDIA_ID = "1501"
MEDIA_TYPE = "CAROUSEL_ALBUM"

TIMESTAMP_UTC = "2025-12-00T15:47:16+0000"   # 업로드 시각
CAPTION = "아들아 연락하지 마"

PERMALINK = "dummy"

COLLECT_START = "2025-12-15 15:46:13"
COLLECT_INTERVAL_MIN = 10

# =============================
# 1. 디지타이징 CSV 로드
# =============================
INPUT_CSV = "C:/dizitizing/before_dizitizing(excel)/01/15-1.csv"
df = pd.read_csv(INPUT_CSV)

# 앞 두 컬럼을 x, views로 사용
x = df.iloc[:, 0].values
y = df.iloc[:, 1].values

# =============================
# 2. 누적성 보정
# =============================
y_mono = np.maximum.accumulate(y)

# =============================
# 3. 1008 포인트 리샘플링
# =============================
N_TARGET = 1008
x_new = np.linspace(x.min(), x.max(), N_TARGET)
views_new = np.interp(x_new, x, y_mono).astype(int)

# =============================
# 4. collected_at 생성
# =============================
start_time = datetime.strptime(COLLECT_START, "%Y-%m-%d %H:%M:%S")
collected_at = [
    (start_time + timedelta(minutes=i * COLLECT_INTERVAL_MIN))
    .strftime("%Y-%m-%d %H:%M:%S.000 UTC")
    for i in range(N_TARGET)
]

# =============================
# 5. 최종 DataFrame (컬럼 분리!)
# =============================
df_out = pd.DataFrame({
    "media_id": MEDIA_ID,
    "media_type": MEDIA_TYPE,
    "timestamp_utc": TIMESTAMP_UTC,
    "caption": CAPTION,
    "permalink": PERMALINK,
    "views": views_new,
    "collected_at": collected_at
})

# =============================
# 6. CSV 저장
# =============================
OUTPUT_CSV = "C:/dizitizing/after_dizitizing(excel)/01/15-01.csv"
df_out.to_csv(OUTPUT_CSV, index=False)

print("스키마 분리 완료 + 실제 로그 형태 CSV 생성")
print(df_out.head())