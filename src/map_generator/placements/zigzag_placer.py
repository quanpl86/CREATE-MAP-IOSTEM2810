# src/map_generator/placements/zigzag_placer.py

import random
from .base_placer import BasePlacer
from src.map_generator.models.path_info import PathInfo

class ZigzagPlacer(BasePlacer):
    """
    Đặt các vật phẩm cho các map có dạng ziczac.
    
    Placer này được thiết kế để hoạt động với ZigzagTopology, đảm bảo
    vật phẩm được đặt ở một vị trí hợp lý trên đường đi, không trùng với
    điểm bắt đầu hoặc kết thúc.
    """

    def place_items(self, path_info: PathInfo, params: dict) -> dict:
        """
        Nhận một con đường ziczac và đặt một vật phẩm lên một điểm ngẫu nhiên
        trên con đường đó.

        Args:
            path_info (PathInfo): Thông tin đường đi từ ZigzagTopology.
            params (dict): Các tham số bổ sung.

        Returns:
            dict: Một dictionary chứa layout map hoàn chỉnh.
        """
        print("    LOG: Placing items with 'zigzag' logic...")

        items = []
        # Lấy tất cả các tọa độ có thể đặt, loại trừ điểm đầu và điểm cuối
        possible_placement_coords = [coord for coord in path_info.path_coords if coord != path_info.start_pos and coord != path_info.target_pos]

        # [CẢI TIẾN] Đặt nhiều vật phẩm dựa trên item_count từ params
        num_items = params.get('item_count', 1) # Mặc định là 1 nếu không có

        if possible_placement_coords:
            selected_coords = random.sample(possible_placement_coords, min(num_items, len(possible_placement_coords)))
            items.extend([{"type": "crystal", "pos": pos} for pos in selected_coords])

        return {
            "start_pos": path_info.start_pos,
            "target_pos": path_info.target_pos,
            "items": items,
            "obstacles": path_info.obstacles
        }