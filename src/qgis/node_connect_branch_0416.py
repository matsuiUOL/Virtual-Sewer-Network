from qgis.core import QgsProject, QgsPointXY, QgsLineString
from qgis.PyQt.QtCore import QVariant

# ノードとブランチのレイヤを取得
nodes_layer = QgsProject.instance().mapLayersByName('Nodes_xyz')[0]
branches_layer = QgsProject.instance().mapLayersByName('Branches')[0]

# ブランチレイヤに接続ノードIDを保存するフィールドを追加
branches_layer.dataProvider().addAttributes([QgsField("start_node_id", QVariant.Int),
                                             QgsField("end_node_id", QVariant.Int)])
branches_layer.updateFields()

# 編集モードの開始
if not branches_layer.isEditable():
    branches_layer.startEditing()

# 削除するフィーチャを保持するリスト
features_to_delete = []

# 各ブランチの端点をノードに結び付けてIDを保存
for branch in branches_layer.getFeatures():
    branch_geom = branch.geometry()

    # ラインジオメトリを取得し、QgsLineStringに変換
    if branch_geom.isMultipart():
        line = branch_geom.asMultiPolyline()[0]  # マルチパートの場合
    else:
        line = branch_geom.asPolyline()  # 単一のラインの場合

    # ブランチの始点と終点を取得
    start_point = line[0]  # 最初の頂点
    end_point = line[-1]  # 最後の頂点

    # 始点と終点に最も近いノードを検索
    closest_start_node = None
    closest_end_node = None
    min_start_dist = float('inf')
    min_end_dist = float('inf')

    for node in nodes_layer.getFeatures():
        node_geom = node.geometry().asPoint()
        node_id = node['Nodes_id']  # ノードID

        # 距離を計算して最も近いノードを特定
        start_dist = QgsPointXY(start_point).distance(node_geom)
        end_dist = QgsPointXY(end_point).distance(node_geom)

        if start_dist < min_start_dist:
            min_start_dist = start_dist
            closest_start_node = node_id

        if end_dist < min_end_dist:
            min_end_dist = end_dist
            closest_end_node = node_id

    # 属性テーブルにノードIDを保存
    branch['start_node_id'] = closest_start_node
    branch['end_node_id'] = closest_end_node
    branches_layer.updateFeature(branch)

    # ブランチの長さを"Length"フィールドから取得
    #branch_length = branch['Length']

    # 始点と終点が同じ場合、#または長さが2.0未満の場合は削除リストに追加
    if closest_start_node == closest_end_node #or branch_length < 2.0:
        features_to_delete.append(branch.id())

# 削除リストにあるブランチを削除
branches_layer.dataProvider().deleteFeatures(features_to_delete)

# 変更を保存して編集モードを終了
if branches_layer.isEditable():
    branches_layer.commitChanges()
else:
    print("Failed to start editing the layer")

# 結果を確認
for branch in branches_layer.getFeatures():
    print(f"Branch ID: {branch['Branches_id']}, Start Node ID: {branch['start_node_id']}, End Node ID: {branch['end_node_id']}, Length: {branch['Length']}")
