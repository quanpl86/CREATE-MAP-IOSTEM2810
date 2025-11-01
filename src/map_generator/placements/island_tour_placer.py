# src/map_generator/placements/island_tour_placer.py

import random
from .base_placer import BasePlacer
from src.map_generator.models.path_info import PathInfo

class IslandTourPlacer(BasePlacer):
    """
    Placer chuyên dụng cho các map có nhiều đảo và bậc thang.
    Logic chính là chỉ đặt vật phẩm trên các "hòn đảo" (khu vực bằng phẳng),
    bỏ qua các bậc thang và cầu nối, để người chơi tập trung vào việc điều hướng.
    """

    def place_items(self, path_info: PathInfo, params: dict) -> dict:
        """
        Đặt vật phẩm lên các hòn đảo.

        Args:
            path_info (PathInfo): Thông tin từ Topology (hub_with_stepped_islands, etc.).
            params (dict): Các tham số bổ sung.

        Returns:
            dict: Layout map hoàn chỉnh.
        """
        print("    LOG: Placing items with 'island_tour' logic...")

        items = []
        # Kế thừa các chướng ngại vật (bậc thang) đã được Topology tạo ra.
        obstacles = path_info.obstacles.copy()

        # Xác định các "hòn đảo" bằng cách tìm các khu vực bằng phẳng trong placement_coords.
        # Một cách đơn giản là giả định các khối không phải bậc thang là đảo.
        # [SỬA LỖI] Loại bỏ cả vị trí bắt đầu và kết thúc khỏi danh sách các ô có thể đặt vật phẩm.
        stair_coords = {obs['pos'] for obs in obstacles}
        island_coords = [p for p in path_info.placement_coords if p not in stair_coords 
                         and p != path_info.start_pos and p != path_info.target_pos]

        # Đặt vật phẩm ngẫu nhiên trên các hòn đảo.
        # Có thể cải tiến để đặt 1 vật phẩm trên mỗi đảo.
        num_items = params.get('item_count', len(island_coords)) # Mặc định đặt đầy
        
        selected_coords = random.sample(island_coords, min(num_items, len(island_coords)))
        items.extend([{"type": "crystal", "pos": pos} for pos in selected_coords])

        return {
            "start_pos": path_info.start_pos,
            "target_pos": path_info.target_pos,
            "items": items,
            "obstacles": obstacles
        }