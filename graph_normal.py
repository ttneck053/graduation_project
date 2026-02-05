import pandas as pd
import matplotlib.pyplot as plt
#정규화 컨텐츠 조회수 곡선 그래프

# =========================
# 기본 설정
# =========================
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

DATA_PATH = "C:/graduration_project/data/data.csv"
MAX_T = 1008

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

dep_config = {
    "red":   {"title": "상위 10%", "color": "red"},
    "green": {"title": "중간값 80%", "color": "green"},
    "blue":  {"title": "하위 10%", "color": "blue"},
}

# =========================
# 공통 grid 스타일
# =========================
GRID_ALPHA = 0.25
GRID_LINEWIDTH = 0.8

# =========================
# 1️⃣ 전체 콘텐츠 그래프 (정규화 + deps 색상 + 통계)
# =========================
plt.figure(figsize=(16, 8))

for media_id, g in valid_df.groupby("media_id"):
    g = g.reset_index(drop=True).iloc[:MAX_T]
    g["t"] = range(len(g))

    y = g["views"] / g["views"].max()  # 정규화

    plt.plot(
        g["t"],
        y,
        color=media_dep[media_id],
        alpha=0.18,
        linewidth=1
    )

# 전체 통계 (실제 조회수 기준)
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
    transform=plt.gca().transAxes,
    fontsize=11,
    verticalalignment="top",
    bbox=dict(boxstyle="round", facecolor="white", alpha=0.85)
)

plt.title("곡선 그래프 : 전체 콘텐츠(상위 - 빨강, 중위 - 파랑, 하위 - 초록)")
plt.xlabel("시간 (1point 당 10분)")
plt.ylabel("정규화된 누적 조회수")
plt.ylim(0, 1.02)
plt.grid(True, alpha=GRID_ALPHA, linewidth=GRID_LINEWIDTH)
plt.show()

print("전체 콘텐츠 곡선 수:", total_cnt)
print()

# =========================
# 2️⃣ deps별 그래프 (정규화 + 통계)
# =========================
for dep, cfg in dep_config.items():
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

        y = g["views"] / g["views"].max()

        plt.plot(
            g["t"],
            y,
            color=cfg["color"],
            alpha=0.25,
            linewidth=1
        )

    plt.text(
        0.02, 0.95,
        f"곡선 수: {count}개\n"
        f"평균 조회수: {mean_v:,.0f}\n"
        f"최소 조회수: {min_v:,.0f}\n"
        f"최대 조회수: {max_v:,.0f}",
        transform=plt.gca().transAxes,
        fontsize=11,
        verticalalignment="top",
        bbox=dict(boxstyle="round", facecolor="white", alpha=0.85)
    )

    plt.title(f"곡선 그래프 : {cfg['title']} (정규화)")
    plt.xlabel("시간 (1point 당 10분)")
    plt.ylabel("정규화된 누적 조회수")
    plt.ylim(0, 1.02)
    plt.grid(True, alpha=GRID_ALPHA, linewidth=GRID_LINEWIDTH)
    plt.show()

# =========================
# deps 분포 요약
# =========================
print("===== deps 분포 =====")
print(media_dep.value_counts())