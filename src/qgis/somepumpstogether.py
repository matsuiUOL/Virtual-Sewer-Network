from qgis.core import (
    QgsProject,
    QgsField,
    QgsFeature,
    QgsPointXY
)
from PyQt5.QtCore import QVariant
import math

# 1. レイヤーの取得
layer = QgsProject.instance().mapLayersByName('Nodes_NP1')[0]

# 2. Node A, B, C のIDと距離制限を設定
node_settings = {
    7494: 1100,  # NodeA (ID = 389, 距離 = 1100m)
    3003: 1500,   # NodeB (ID = 77, 距離 = 1500m)
    9696: 290     # NodeC (ID = 55, 距離 = 290m)
}

# 最大深さと最小深さの設定
max_depth = 5.0  # 最大深さ (m)
min_depth = 3.0  # 最小深さ (m)

# 3. フィールドの追加 (距離フィールドと深さフィールド)
layer_provider = layer.dataProvider()
for node_id in node_settings.keys():
    dist_field = f"dist_{node_id}"
    depth_field = f"depth_{node_id}"
    existing_fields = [field.name() for field in layer.fields()]
    
    if dist_field not in existing_fields:
        layer_provider.addAttributes([QgsField(dist_field, QVariant.Double)])
    if depth_field not in existing_fields:
        layer_provider.addAttributes([QgsField(depth_field, QVariant.Double)])

layer.updateFields()

# 4. 基準ノードの座標を取得
node_coordinates = {}
for feature in layer.getFeatures():
    node_id = feature['Nodes_id']
    if node_id in node_settings.keys():
        geom = feature.geometry()
        node_coordinates[node_id] = QgsPointXY(geom.asPoint().x(), geom.asPoint().y())

# 5. 距離と深さの計算
layer.startEditing()
for feature in layer.getFeatures():
    feature_geom = feature.geometry()
    feature_point = QgsPointXY(feature_geom.asPoint().x(), feature_geom.asPoint().y())
    feature_updated = False

    for node_id, max_distance in node_settings.items():
        # 基準ノードの座標を取得
        if node_id not in node_coordinates:
            continue
        
        base_point = node_coordinates[node_id]

        # ユークリッド距離を計算
        distance = math.sqrt((feature_point.x() - base_point.x())**2 +
                             (feature_point.y() - base_point.y())**2)
        
        # 距離が範囲内の場合、距離と深さを計算
        if distance <= max_distance:
            # 距離フィールドを更新
            feature[f"dist_{node_id}"] = distance
            
            # 深さを線形補間して計算
            interpolated_depth = max_depth - (max_depth - min_depth) * (distance / max_distance)
            feature[f"depth_{node_id}"] = interpolated_depth
            feature_updated = True

    # 更新された場合、フィーチャーを保存
    if feature_updated:
        layer.updateFeature(feature)

layer.commitChanges()
print("処理が完了しました。")
