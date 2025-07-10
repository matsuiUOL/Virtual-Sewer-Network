import pandas as pd
import networkx as nx

# データ読み込み
nodes_df = pd.read_csv("nodes.csv")  # outlet_id列が追加済み
branches_df = pd.read_csv("branches.csv")  # start_node_id, end_node_id, Branches_id, Lengthなど

# 空のリストに各outletごとの有向木を格納
all_directed_trees = []

# outletごとの処理
for outlet in nodes_df['outlet_id'].dropna().unique():
    outlet = int(outlet)

    # このoutletに属するノード一覧
    sub_nodes = nodes_df[nodes_df['outlet_id'] == outlet]['Nodes_id'].tolist()

    # 関連するブランチのみ抽出
    sub_branches = branches_df[
        branches_df['start_node_id'].isin(sub_nodes) &
        branches_df['end_node_id'].isin(sub_nodes)
    ]

    # 無向グラフの構築（MST用）
    G_sub = nx.Graph()
    for _, row in sub_branches.iterrows():
        G_sub.add_edge(row['start_node_id'], row['end_node_id'],
                       weight=row['Length'], branch_id=row['Branches_id'])

    if not nx.is_connected(G_sub):
        # 非連結な場合：コンポーネントごとに処理
        components = list(nx.connected_components(G_sub))
    else:
        components = [G_sub.nodes]

    for comp_nodes in components:
        G_comp = G_sub.subgraph(comp_nodes)
        if len(G_comp.nodes) <= 1:
            continue

        # MST作成（無向）
        mst = nx.minimum_spanning_tree(G_comp)

        # outlet がこのコンポーネントに含まれているときだけ有向木を作成
        if outlet in mst.nodes:
            directed_tree = nx.bfs_tree(mst, source=outlet)  # outletに向かう有向木

            # 元の枝情報を引き継ぎ（属性コピー）
            for u, v in directed_tree.edges():
                if mst.has_edge(u, v):
                    data = mst.get_edge_data(u, v)
                else:
                    data = mst.get_edge_data(v, u)  # 無向エッジなので反対向きも確認
                directed_tree[u][v].update(data)

            all_directed_trees.append(directed_tree)

# 複数の有向木を統合した全体グラフ
combined_directed_graph = nx.compose_all(all_directed_trees)

# 結果出力：ブランチ一覧
# 有向枝としての出力（from_node → to_node）
directed_branches = []
for u, v, data in combined_directed_graph.edges(data=True):
    directed_branches.append({
        'from_node': u,
        'to_node': v,
        'Branches_id': data.get('branch_id'),
        'Length': data.get('weight')
    })

# 出力：向きをつけたブランチ情報
branch_directions_df = pd.DataFrame(directed_branches)
branch_directions_df.to_csv("Branch_directions.csv", index=False)


# 結果出力：ノード一覧
used_nodes = [{'Nodes_id': n} for n in combined_directed_graph.nodes()]
nodes_output_df = pd.DataFrame(used_nodes)
nodes_output_df.to_csv("final_used_nodes_directed.csv", index=False)
