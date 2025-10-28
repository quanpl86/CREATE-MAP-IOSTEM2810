# src/map_generator/placements/spiral_3d_placer.py

import random
from .base_placer import BasePlacer
from src.map_generator.models.path_info import PathInfo

class Spiral3DPlacer(BasePlacer):
    """
    Đặt vật phẩm cho map xoắn ốc 3D.
    """
    def place_items(self, path_info: PathInfo, params: dict) -> dict:
        print("    LOG: Placing items with 'spiral_3d' logic...")

        item_count = params.get('item_count', 8)
        item_type = params.get('item_type', 'crystal')

        possible_coords = [p for p in path_info.path_coords if p != path_info.start_pos and p != path_info.target_pos]
        selected_coords = random.sample(possible_coords, min(item_count, len(possible_coords)))
        items = [{"type": item_type, "pos": pos} for pos in selected_coords]

        return {"start_pos": path_info.start_pos, "target_pos": path_info.target_pos, "items": items, "obstacles": path_info.obstacles}