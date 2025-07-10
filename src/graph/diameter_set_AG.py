import pandas as pd
import networkx as nx

# ① データ読み込み
nodes_df = pd.read_csv("filtered_nodes.csv")
branches_df = pd.read_csv("Branch_directions.csv")

# ② outletごとの設計適用範囲（距離[m]）を定義：ローカルに設定する
design_ranges = {
    1370: 1200,
    3894: 600,
    3213: 300,
    1532: 150,
    817: 1200,
    2254: 400,
    2328: 150

}
# outletごとの最大管径（mm）を定義
max_diameters = {
    1370: 3000,
    3894: 3000,
    3213: 3000,
    1532: 3000,
    817: 3000,
    2254: 3000,
    2328: 3000
}


# --- ノードごとの座標辞書を作成 ---
node_coords = nodes_df.set_index("Nodes_id")[["xcoord", "ycoord"]].to_dict("index")

# --- outlet_id をノード ID に対応づけ（逆引き） ---
node_to_outlet = nodes_df.set_index("Nodes_id")["outlet_id"].to_dict()


# --- 各ブランチの中点距離を計算 ---
def calc_avg_distance(n1, n2):
    if n1 not in node_coords or n2 not in node_coords:
        return None  # 対象外ノード（出力対象にしない）
    x1, y1 = node_coords[n1]["xcoord"], node_coords[n1]["ycoord"]
    x2, y2 = node_coords[n2]["xcoord"], node_coords[n2]["ycoord"]
    return ((x1 + x2) / 2, (y1 + y2) / 2)

# --- 管径を計算 ---
def calc_diameter(avg_dist, outlet_id):
    if outlet_id not in design_ranges or avg_dist is None:
        return 600  # 設計適用外 or エラー → 最小管径

    # 中心点のノード距離を outlet ノードと比較して距離を出す
    outlet_coords = node_coords.get(outlet_id)
    if not outlet_coords:
        return 600

    ox, oy = outlet_coords["xcoord"], outlet_coords["ycoord"]
    dx, dy = avg_dist[0] - ox, avg_dist[1] - oy
    dist = (dx**2 + dy**2)**0.5

    max_dist = design_ranges[outlet_id]
    max_diameter = max_diameters.get(outlet_id, 3000)  # ←ここで値を取得
    if dist > max_dist:
        return 600
    else:
        # 線形補間（最大→3000、最小→600）
        return int(600 + (max_dist - dist) / max_dist * (max_diameter - 600))

diameters = []

for _, row in branches_df.iterrows():
    from_id = row["from_node"]
    to_id = row["to_node"]

    from_outlet = node_to_outlet.get(from_id)
    to_outlet = node_to_outlet.get(to_id)

    # 両端ノードが同じ outlet に属しているか確認
    if from_outlet is not None and to_outlet is not None and from_outlet == to_outlet:
        outlet_id = from_outlet
        avg_dist = calc_avg_distance(from_id, to_id)  # 中点座標を取得

        diameter = calc_diameter(avg_dist, outlet_id)
    else:
        diameter = 600  # outlet が一致しない、またはノード情報が不完全

    diameters.append(diameter)

# 結果を保存
branches_df["diameter"] = diameters
branches_df.to_csv("Branch_with_diameter.csv", index=False)
print("Branch_with_diameter.csv に保存しました。")
