# src/map_generator/placements/triangle_placer.py

import random
from .base_placer import BasePlacer
from src.map_generator.models.path_info import PathInfo

class TrianglePlacer(BasePlacer):
    """
    Đặt các vật phẩm cho các map có dạng tam giác.
    Placer này đảm bảo vật phẩm được đặt ở các vị trí hợp lý trên
    các cạnh của tam giác, không trùng với điểm bắt đầu, góc hoặc kết thúc.
    """

    def place_items(self, path_info: PathInfo, params: dict) -> dict:
        """
        Nhận một con đường tam giác và đặt vật phẩm lên đó.

        Args:
            path_info (PathInfo): Thông tin đường đi từ TriangleTopology.
            params (dict): Các tham số bổ sung (ví dụ: item_count).

        Returns:
            dict: Một dictionary chứa layout map hoàn chỉnh.
        """
        print("    LOG: Placing items with 'triangle' logic...")

        items = []
        item_count = params.get('item_count', 3) # Mặc định đặt 3 vật phẩm

        # [SỬA LỖI] Lọc ra các vị trí có thể đặt vật phẩm.
        # Loại bỏ vị trí bắt đầu và kết thúc để tránh đặt vật phẩm trùng lặp.
        coords_for_items = [
            p for p in path_info.placement_coords 
            if p != path_info.start_pos and p != path_info.target_pos
        ]

        if coords_for_items:
            # Chọn ngẫu nhiên 'item_count' vị trí từ các vị trí có thể
            selected_coords = random.sample(coords_for_items, min(item_count, len(coords_for_items)))
            for pos in selected_coords:
                items.append({"type": "crystal", "pos": pos})

        return {
            "start_pos": path_info.start_pos,
            "target_pos": path_info.target_pos,
            "items": items,
            "obstacles": path_info.obstacles
        }