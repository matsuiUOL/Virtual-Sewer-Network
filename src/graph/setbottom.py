import pandas as pd
import networkx as nx
import numpy as np

# ファイル読み込み
nodes_df = pd.read_csv("nodes.csv")
branches_df = pd.read_csv("Branch_directions.csv")

# outlet ノードを取得
outlet_ids = nodes_df['outlet_id'].dropna().unique()
outlet_node_ids = nodes_df[nodes_df['outlet_id'].isin(outlet_ids)]['Nodes_id'].astype(int).tolist()

# 有向グラフを構築（from_node → to_node）
G = nx.DiGraph()
for _, row in branches_df.iterrows():
    G.add_edge(int(row['from_node']), int(row['to_node']))

# outlet ノードからすべてのノードへの距離を計算（逆方向）
longest_distances = {}
for outlet in outlet_node_ids:
    lengths = nx.single_target_shortest_path_length(G, outlet)
    longest_distances.update(lengths)

# 最大距離で正規化し、深さ（3～5m）を線形補間
max_distance = max(longest_distances.values())
depths = {
    node_id: 3.0 + (dist / max_distance) * (5.0 - 3.0)
    for node_id, dist in longest_distances.items()
}

# nodes_df にマンホール深さ・管底高を追加
nodes_df["manhole_depth"] = nodes_df["Nodes_id"].map(depths)
nodes_df["invert_elevation"] = nodes_df["z"] - nodes_df["manhole_depth"]

# NaNになったノード（グラフに含まれない）に対してはdepth=3mと仮定
nodes_df["manhole_depth"].fillna(3.0, inplace=True)
nodes_df["invert_elevation"].fillna(nodes_df["z"] - 3.0, inplace=True)

# 保存
nodes_df.to_csv("nodes_with_invert.csv", index=False)

# 確認表示
print(nodes_df[["Nodes_id", "z", "manhole_depth", "invert_elevation"]].head())
