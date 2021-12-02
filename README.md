# ChestSearch
Amulet Editor用プラグイン  
チェストやかまど等のアイテムを格納することができるタイルエンティティの座標を検索する
中身が空であることやルートテーブルが設定されていることなども出力されます

## 配置場所
AmuletEditorの`plugins/operations`に配置してください。

## 検索方法
1.AmuletEditorを起動し、3DEditorのoperationsから`チェスト検索`を選択する。

2.`検索開始`ボタンを押下する。

3.検索が完了するまで待つ。

4.検索が完了したら、AmuletEditorの実行ファイルと同じ階層のディレクトリにChestSearchのディレクトリが作成されます。

5.ChestSearchディレクトリに`YYYYMMDDHHMMSS.csv`の形式でCSVが出力されます。（検索を開始した日時）
