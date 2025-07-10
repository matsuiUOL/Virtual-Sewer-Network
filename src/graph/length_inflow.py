import pandas as pd
import networkx as nx

# パラメータ設定
rain_intensity = 60 / 3600 / 1000  # 60 mm/h → m/s
grating_area_per_length = 0.1     # m²/m（仮定）

# ファイル読み込み
nodes_df = pd.read_csv("nodes.csv")
branches_df = pd.read_csv("branches.csv")
directions_df = pd.read_csv("Branch_directions.csv")  # 向き情報の読み込み

# 各枝の局所的な流入量を計算
branches_df['local_inflow'] = branches_df['Length'] * grating_area_per_length * rain_intensity

# 有向グラフ構築（向きに従って）
G = nx.DiGraph()
branch_id_to_local_inflow = {}

for _, row in directions_df.iterrows():
    from_node = int(row['from_node'])
    to_node = int(row['to_node'])
    branch_id = int(row['Branches_id'])

    branch_info = branches_df[branches_df['Branches_id'] == branch_id].iloc[0]
    local_inflow = branch_info['local_inflow']
    branch_id_to_local_inflow[branch_id] = local_inflow

    G.add_edge(from_node, to_node,
               branch_id=branch_id,
               inflow=local_inflow)

# トポロジカルソート（上流→下流順）
try:
    topo_order = list(nx.topological_sort(G))
except nx.NetworkXUnfeasible:
    print("グラフに閉路が含まれています。流量伝播を実行できません。")
    exit()

# ノードごとの流量（ノードに到達したときの合計流量）
node_flow = {}

# ブランチごとの流量
branch_flow = {}

# 流量伝播処理
for node in topo_order:
    # このノードに入ってくる流量の合計（初期は0）
    incoming_flow = 0
    for pred in G.predecessors(node):
        edge_data = G.edges[pred, node]
        branch_id = edge_data['branch_id']
        incoming_flow += branch_flow.get(branch_id, 0)

    # このノードを出ていく各ブランチに流量を渡す
    for succ in G.successors(node):
        edge_data = G.edges[node, succ]
        branch_id = edge_data['branch_id']
        local_inflow = edge_data['inflow']
        total_flow = incoming_flow + local_inflow
        branch_flow[branch_id] = total_flow

# 結果を DataFrame に格納
branches_df['flow_rate'] = branches_df['Branches_id'].map(branch_flow)

# 保存
branches_df.to_csv("Branches_with_flow.csv", index=False)

# 確認表示
print(branches_df[['Branches_id', 'Length', 'local_inflow', 'flow_rate']].head(5))
