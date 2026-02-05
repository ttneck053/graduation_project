import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
# 비정규화 컨텐츠 조회수 곡선 그래프

# =========================
# 기본 설정
# =========================
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

DATA_PATH = "C:/graduration_project/data/data.csv"
MAX_T = 1000

# =========================
# 데이터 로드 & 정렬
# =========================
df = pd.read_csv(DATA_PATH)
df["collected_at"] = pd.to_datetime(df["collected_at"])
df = df.sort_values(["media_id", "collected_at"])

# =========================
# 유효 콘텐츠 필터
# =========================
valid_df = (
    df.groupby("media_id")
      .filter(lambda g: len(g) >= MAX_T and g["views"].max() > 0)
      .sort_values(["media_id", "collected_at"])
)

# =========================
# deps 분류 (최종 조회수 기준)
# =========================
final_views = valid_df.groupby("media_id")["views"].last()
q10 = final_views.quantile(0.10)
q90 = final_views.quantile(0.90)

def get_dep(v):
    if v >= q90:
        return "red"      # 상위 10%
    elif v < q10:
        return "blue"     # 하위 10%
    else:
        return "green"    # 중간 80%

media_dep = final_views.apply(get_dep)

# =========================
# deps 설정 (Y축 단위 포함)
# =========================
dep_config = {
    "all": {
        "title": "전체 콘텐츠",
        "color": None,
        "y_step": 1_000_000
    },
    "red": {
        "title": "상위 10%",
        "color": "red",
        "y_step": 200_000
    },
    "green": {
        "title": "중위 80%",
        "color": "green",
        "y_step": 20_000
    },
    "blue": {
        "title": "하위 10%",
        "color": "blue",
        "y_step": 2_000
    }
}

# =========================
# 공통 grid 스타일
# =========================
GRID_ALPHA = 0.25
GRID_LINEWIDTH = 0.8

# =========================
# 1️⃣ 전체 콘텐츠 그래프 (비정규화)
# =========================
plt.figure(figsize=(16, 8))

for media_id, g in valid_df.groupby("media_id"):
    g = g.reset_index(drop=True).iloc[:MAX_T]
    g["t"] = range(len(g))

    plt.plot(
        g["t"],
        g["views"],
        color=media_dep[media_id],
        alpha=0.15,
        linewidth=1
    )

ax = plt.gca()
ax.yaxis.set_major_locator(MultipleLocator(dep_config["all"]["y_step"]))

# 전체 통계
mean_v = final_views.mean()
min_v = final_views.min()
max_v = final_views.max()
total_cnt = final_views.shape[0]

plt.text(
    0.02, 0.95,
    f"곡선 수: {total_cnt}개\n"
    f"평균 조회수: {mean_v:,.0f}\n"
    f"최소 조회수: {min_v:,.0f}\n"
    f"최대 조회수: {max_v:,.0f}",
    transform=ax.transAxes,
    fontsize=11,
    verticalalignment="top",
    bbox=dict(boxstyle="round", facecolor="white", alpha=0.85)
)

plt.title("곡선 그래프 : 전체 콘텐츠 (비정규화)")
plt.xlabel("시간 (1point 당 10분)")
plt.ylabel("누적 조회수")
plt.grid(True, alpha=GRID_ALPHA, linewidth=GRID_LINEWIDTH)
plt.show()

# =========================
# 2️⃣ deps별 그래프 (비정규화)
# =========================
for dep in ["red", "green", "blue"]:
    cfg = dep_config[dep]
    plt.figure(figsize=(16, 8))

    dep_ids = media_dep[media_dep == dep].index
    stats = final_views.loc[dep_ids]

    mean_v = stats.mean()
    min_v = stats.min()
    max_v = stats.max()
    count = len(stats)

    for media_id in dep_ids:
        g = valid_df[valid_df["media_id"] == media_id]
        g = g.reset_index(drop=True).iloc[:MAX_T]
        g["t"] = range(len(g))

        plt.plot(
            g["t"],
            g["views"],
            color=cfg["color"],
            alpha=0.25,
            linewidth=1
        )

    ax = plt.gca()
    ax.yaxis.set_major_locator(MultipleLocator(cfg["y_step"]))

    plt.text(
        0.02, 0.95,
        f"곡선 수: {count}개\n"
        f"평균 조회수: {mean_v:,.0f}\n"
        f"최소 조회수: {min_v:,.0f}\n"
        f"최대 조회수: {max_v:,.0f}",
        transform=ax.transAxes,
        fontsize=11,
        verticalalignment="top",
        bbox=dict(boxstyle="round", facecolor="white", alpha=0.85)
    )

    plt.title(f"곡선 그래프 : {cfg['title']} (비정규화)")
    plt.xlabel("시간 (1point 당 10분)")
    plt.ylabel("누적 조회수")
    plt.grid(True, alpha=GRID_ALPHA, linewidth=GRID_LINEWIDTH)
    plt.show()

# =========================
# deps 분포 요약
# =========================
print("===== deps 분포 =====")
print(media_dep.value_counts())