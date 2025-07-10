import pandas as pd

# ファイルの読み込み
used_nodes = pd.read_csv("final_used_nodes_directed.csv")
all_nodes = pd.read_csv("nodes.csv")

# Nodes_id の共通部分でフィルタ
filtered_nodes = all_nodes[all_nodes["Nodes_id"].isin(used_nodes["Nodes_id"])]

# 結果を新しいCSVとして保存
filtered_nodes.to_csv("filtered_nodes.csv", index=False)

print("filtered_nodes.csv に保存しました。")
