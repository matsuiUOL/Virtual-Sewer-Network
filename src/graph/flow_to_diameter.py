import pandas as pd
import math

# CSV読み込み
df = pd.read_csv("Branches_with_flow.csv")

# flow_rateの最大・最小（NaNを除外）
max_flow = df["flow_rate"].max(skipna=True)
min_flow = df["flow_rate"].min(skipna=True)

# 線形補間関数（NaNチェック付き）
def interpolate_diameter(flow, min_flow, max_flow, min_d=600, max_d=3000):
    if pd.isna(flow):
        return None  # 欠損値の場合は None を返す（あとで扱いやすく）
    if max_flow == min_flow:
        return min_d
    interpolated = min_d + (flow - min_flow) * (max_d - min_d) / (max_flow - min_flow)
    return int(round(interpolated))

# diameter列を作成
df["diameter"] = df["flow_rate"].apply(lambda f: interpolate_diameter(f, min_flow, max_flow)).astype("Int64")

# CSV出力
df.to_csv("Branches_with_diameter.csv", index=False)

# 確認出力
print(df[["Branches_id", "flow_rate", "diameter"]].head())

