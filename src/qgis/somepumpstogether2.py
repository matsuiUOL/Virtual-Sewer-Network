from qgis.core import QgsProject, QgsField
from PyQt5.QtCore import QVariant

# 1. レイヤーの取得
layer = QgsProject.instance().mapLayersByName('Nodes_NP1')[0]

# 2. フィールド名リストを取得（デバッグ用にすべて表示）
field_names = [field.name() for field in layer.fields()]
print(f"Available fields: {field_names}")  # デバッグ: 利用可能なフィールド名を表示

# 3. mh_depth フィールドが存在しない場合は追加
if 'mh_depth' not in field_names:
    layer.dataProvider().addAttributes([QgsField('mh_depth', QVariant.Double)])
    layer.updateFields()

# 4. フィーチャを処理して、mh_depth に値を設定
layer.startEditing()
for feature in layer.getFeatures():
    mh_depth_value = None

    # 各mh_フィールドに値が格納されているか確認
    mh_3003 = feature['depth_3003']
    mh_7494 = feature['depth_7494']
    mh_9696 = feature['depth_9696']

    print(f"Processing Node {feature['Nodes_id']}")  # デバッグ: 現在のノードIDを表示

    # いずれかのフィールドに値があれば、その値を mh_depth に設定
    if mh_3003 not in [None, "NULL", "null", ""]:
        mh_depth_value = mh_3003
#        print(f"  Found value in mh_3003: {mh_3003}")
    elif mh_7494 not in [None, "NULL", "null", ""]:
        mh_depth_value = mh_7494
#        print(f"  Found value in mh_7494: {mh_7494}")
    elif mh_9696 not in [None, "NULL", "null", ""]:
        mh_depth_value = mh_9696
#        print(f"  Found value in mh_9696: {mh_9696}")
    else:
      # いずれにも値がない場合、'標高' - 3.12 を mh_depth に設定
        elevation = feature['標高']
        if elevation is not None:
            mh_depth_value = elevation - 3.12
        else:
            mh_depth_value = 3.12  # '標高' が None の場合は 3.12 を設定
 #       print(f"  No value found in depth fields, setting mh_depth to '標高' - 3.12 = {mh_depth_value}")


    # mh_depth に値を設定
    feature['mh_depth'] = mh_depth_value
    layer.updateFeature(feature)

# 5. 編集を保存して終了
layer.commitChanges()
print("mh_depth フィールドに値を統合しました。")
