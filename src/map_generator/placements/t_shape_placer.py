import random
from .base_placer import BasePlacer
from src.map_generator.models.path_info import PathInfo

class TShapePlacer(BasePlacer):
    """
    Đặt các vật phẩm cho các map có dạng chữ T.
    Placer này đặt các vật phẩm dọc theo đường đi, khuyến khích người chơi
    khám phá toàn bộ hình dạng.
    """

    def place_items(self, path_info: PathInfo, params: dict) -> dict:
        """
        Nhận một con đường chữ T và đặt vật phẩm lên đó.

        Args:
            path_info (PathInfo): Thông tin đường đi từ TShapeTopology.
            params (dict): Các tham số bổ sung (ví dụ: item_count).

        Returns:
            dict: Một dictionary chứa layout map hoàn chỉnh.
        """
        print("    LOG: Placing items with 't_shape' logic...")

        item_count = params.get('item_count', 3)
        # [SỬA] Sử dụng placement_coords để có tất cả các ô của hình chữ T
        if path_info.placement_coords:
            possible_coords = [p for p in path_info.placement_coords if p != path_info.start_pos and p != path_info.target_pos]
        else: # Fallback cho an toàn
            possible_coords = [p for p in path_info.path_coords if p != path_info.start_pos and p != path_info.target_pos]
        
        selected_coords = random.sample(possible_coords, min(item_count, len(possible_coords)))
        items = [{"type": "crystal", "pos": pos} for pos in selected_coords]

        return {
            "start_pos": path_info.start_pos,
            "target_pos": path_info.target_pos,
            "items": items,
            "obstacles": path_info.obstacles
        }