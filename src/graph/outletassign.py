import pandas as pd
import networkx as nx

# CSV読み込み
nodes_df = pd.read_csv("nodes.csv")
branches_df = pd.read_csv("branches.csv")
outlets = [553, 817, 1370, 1532, 2254, 2328, 3213, 3894]  # outletのノードIDリスト：ここはローカルに設定する

# 有向グラフ作成
G = nx.Graph()
for _, row in branches_df.iterrows():
    G.add_edge(row['start_node_id'], row['end_node_id'])

# 各ノードから最も近い outlet を探す
def find_nearest_outlet(node):
    min_dist = float('inf')
    nearest_outlet = None
    for outlet in outlets:
        try:
            dist = nx.shortest_path_length(G, source=node, target=outlet)
            if dist < min_dist:
                min_dist = dist
                nearest_outlet = outlet
        except nx.NetworkXNoPath:
            continue
    return nearest_outlet
# 結果を整数型で追加（欠損値は None → NaN）
nodes_df['outlet_id'] = nodes_df['Nodes_id'].map(find_nearest_outlet).astype('Int64')

# CSVに上書き保存
nodes_df.to_csv("nodes.csv", index=False)

# 確認
print(nodes_df[['Nodes_id', 'outlet_id']].head())
