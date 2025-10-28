# src/map_generator/placements/staircase_3d_placer.py

import random
from .base_placer import BasePlacer
from src.map_generator.models.path_info import PathInfo

class Staircase3DPlacer(BasePlacer):
    """
    Đặt vật phẩm lên mỗi bậc của cầu thang 3D.
    """
    def place_items(self, path_info: PathInfo, params: dict) -> dict:
        print("    LOG: Placing items with 'staircase_3d' logic...")

        item_type = params.get('item_type', 'crystal')

        # Đặt một vật phẩm lên mỗi bậc thang, trừ bậc cuối cùng (đích)
        coords_to_place_on = [p for p in path_info.path_coords if p != path_info.target_pos]
        items = [{"type": item_type, "pos": pos} for pos in coords_to_place_on]

        return {"start_pos": path_info.start_pos, "target_pos": path_info.target_pos, "items": items, "obstacles": path_info.obstacles}