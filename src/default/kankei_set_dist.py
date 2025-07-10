import pandas as pd

# 1. データの読み込み
mh_data = pd.read_csv('mh_data.csv')  # MHのデータファイル
sewer_data = pd.read_csv('sewer_data.csv')  # 下水道のデータファイル

# 2. 距離に基づいて管径を計算する関数
def calculate_diameter(distance, pump_type):
    if pump_type == 'pump6' or pump_type == 'pump7' or pump_type == 'pump8':
        min_diameter, max_diameter = 600, 3000
    else:
        min_diameter, max_diameter = 600, 1500

    if distance > 0:
        # 距離に基づく線形補間
        return min_diameter + (max_diameter - min_diameter) * (1 - distance / 1000)
    else:
        return 600  # デフォルトの管径

# 3. 下水道データから、各ポンプ場ごとの距離に基づいて管径を設定
sewer_diameters = []
for _, row in sewer_data.iterrows():
    start_node = row['start_node_id']
    end_node = row['end_node_id']

    # start_node に対応する距離情報を取得
    start_distances = mh_data.loc[mh_data['Nodes_id'] == start_node, [
        'distance_to_pump1', 'distance_to_pump2', 'distance_to_pump3', 'distance_to_pump4', 'distance_to_pump5', 'distance_to_pump6', 'distance_to_pump7', 'distance_to_pump8'
    ]]

    # end_node に対応する距離情報を取得
    end_distances = mh_data.loc[mh_data['Nodes_id'] == end_node, [
        'distance_to_pump1', 'distance_to_pump2', 'distance_to_pump3', 'distance_to_pump4', 'distance_to_pump5', 'distance_to_pump6', 'distance_to_pump7', 'distance_to_pump8'
    ]]

    if start_distances.empty or end_distances.empty:
        print(f"Warning: Node {start_node} or {end_node} has no distance data.")
        diameter = 600  # デフォルトの管径
    else:
        # 距離の平均を計算
        average_distances = (start_distances.values + end_distances.values) / 2
        average_distances = average_distances[0]  # 平均距離の配列を取得

        # 最小の管径を初期化
        diameter = 600

        # 各ポンプ場の距離に基づいて管径を決定
        for i, pump_field in enumerate([
            'distance_to_pump1', 'distance_to_pump2', 'distance_to_pump3', 'distance_to_pump4', 'distance_to_pump5', 'distance_to_pump6', 'distance_to_pump7', 'distance_to_pump8'
        ]):
            if not pd.isna(average_distances[i]):
                pump_type = f"pump{i + 1}"
                diameter = max(diameter, calculate_diameter(average_distances[i], pump_type))

    # 結果をリストに追加
    sewer_diameters.append({
        'Branches_id': row['Branches_id'],
        'start_node_id': start_node,
        'end_node_id': end_node,
        'diameter': int(diameter)
    })

# 4. 計算結果をDataFrameに変換し、CSVとして保存
output_df = pd.DataFrame(sewer_diameters)
output_df.to_csv('sewer_diameters_with_distances.csv', index=False)

# 結果を表示
print(output_df)
