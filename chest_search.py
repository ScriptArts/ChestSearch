import os
from datetime import datetime

import numpy
from amulet import Block, SelectionBox
from typing import TYPE_CHECKING, Tuple, Dict
import wx
from amulet.api.partial_3d_array.base_partial_3d_array import BasePartial3DArray

from amulet_map_editor.api.wx.ui.base_select import EVT_PICK
from amulet_map_editor.api.wx.ui.block_select import BlockDefine
from amulet_map_editor.programs.edit.api.operations import DefaultOperationUI

if TYPE_CHECKING:
    from amulet.api.level import BaseLevel
    from amulet_map_editor.programs.edit.api.canvas import EditCanvas


def _check_block(block: Block, original_base_name: str,
                 original_properties: Dict[str, "WildcardSNBTType"]) -> bool:
    if (block.base_name == original_base_name
            and all(
                original_properties.get(prop) in ["*", val.to_snbt()]
                for prop, val in block.properties.items()
            )
    ):
        return True
    return False


class ChestSearch(wx.Panel, DefaultOperationUI):
    def __init__(
            self, parent: wx.Window, canvas: "EditCanvas", world: "BaseLevel", options_path: str
    ):
        wx.Panel.__init__(self, parent)
        DefaultOperationUI.__init__(self, parent, canvas, world, options_path)

        self.Freeze()
        self._sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self._sizer)

        options = self._load_options({})

        self._description = wx.TextCtrl(
            self, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_BESTWRAP, size=(200, 100)
        )
        self._sizer.Add(self._description, 0, wx.ALL | wx.EXPAND, 5)
        self._description.SetLabel("アイテムが格納可能なタイルエンティティをワールドから全て検索します。\n" +
                                   "検索した内容はEmptyChestSearchディレクトリにCSV形式で出力します。\n" +
                                   "ルートテーブルが設定されているかや、中身が空であるか等も出力します。")
        self._description.Fit()

        self._run_button = wx.Button(self, label="検索開始")
        self._run_button.Bind(wx.EVT_BUTTON, self._run_operation)
        self._sizer.Add(self._run_button, 0, wx.ALL | wx.ALIGN_CENTRE_HORIZONTAL, 5)

        self.Layout()
        self.Thaw()

    @property
    def wx_add_options(self) -> Tuple[int, ...]:
        return (1,)

    def _on_pick_block_button(self, evt):
        self._show_pointer = True

    def disable(self):
        print("Unload EmptyChestSearch")

    def _run_operation(self, _):
        self.canvas.run_operation(
            lambda: self._find_block()
        )

    def _find_block(self):
        world = self.world
        chunk_count = 0
        count = 0
        file_out_list = []
        now = datetime.now()
        directory_name = "ChestSearch"
        filepath = directory_name + "/" + now.strftime("%Y%m%d%H%M%S") + ".csv"

        # 全てのディメンションのチャンク数を取得
        for dimension in world.dimensions:
            chunk_count += len(list(world.all_chunk_coords(dimension)))

        print("ブロック検索プラグイン実行")
        print("総検索チャンク数:" + str(chunk_count))
        print("----------検索開始----------")

        for dimension in world.dimensions:
            for cx, cz in world.all_chunk_coords(dimension):
                chunk = world.get_chunk(cx, cz, dimension)

                for blockEntity in chunk.block_entities:
                    if not blockEntity.nbt["utags"].__contains__("Items"):
                        continue

                    snbt = blockEntity.nbt.to_snbt()
                    x = str(blockEntity.x)
                    y = str(blockEntity.y)
                    z = str(blockEntity.z)
                    is_not_empty = 0
                    is_loottable = 0

                    if len(blockEntity.nbt["utags"]["Items"]) > 0:
                        is_not_empty = 1

                    if blockEntity.nbt["utags"].__contains__("LootTable") and blockEntity.nbt["utags"]["LootTable"] != "":
                        is_loottable = 1

                    base_name = blockEntity.base_name

                    print("X:" + x + " Y:" + y + " Z:" + z + " " + dimension + " " + base_name + " " + snbt)
                    file_out_list.append((x, y, z, dimension, base_name, str(is_not_empty), str(is_loottable)))

                count += 1
                yield count / chunk_count

        print("----------検索終了----------")
        print("検索結果出力 -> " + filepath)

        # ディレクトリ生成
        os.makedirs(directory_name, exist_ok=True)

        # 結果をファイル出力
        with open(filepath, "w") as f:
            f.write("x,y,z,dimension,ブロックの種類,中身の有無,ルートテーブルの有無\n")
            for x, y, z, dimension, base_name, is_not_empty, is_loottable, in file_out_list:
                f.write(x + "," + y + "," + z + "," + dimension + "," + base_name + "," + is_not_empty + "," + is_loottable + "\n")

        wx.MessageBox("検索が完了しました。\n出力先：" + filepath, "検索完了")


export = {
    "name": "チェスト検索",  # the name of the plugin
    "operation": ChestSearch,  # the actual function to call when running the plugin
}
