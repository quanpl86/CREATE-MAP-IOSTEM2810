import random
from .base_placer import BasePlacer
from src.map_generator.models.path_info import PathInfo

class HShapePlacer(BasePlacer):
    """
    Đặt các vật phẩm cho các map có dạng chữ H.
    Placer này đặt các vật phẩm trên tất cả các phần của chữ H,
    khuyến khích người chơi sử dụng hàm để xử lý các phần lặp lại.
    """

    def place_items(self, path_info: PathInfo, params: dict) -> dict:
        """
        Nhận một con đường chữ H và đặt vật phẩm lên đó.

        Args:
            path_info (PathInfo): Thông tin đường đi từ HShapeTopology.
            params (dict): Các tham số bổ sung (ví dụ: item_count, item_type).

        Returns:
            dict: Một dictionary chứa layout map hoàn chỉnh.
        """
        print("    LOG: Placing items with 'h_shape' logic...")

        item_count = params.get('item_count', 5) # Mặc định đặt 5 vật phẩm
        item_type = params.get('item_type', 'crystal')

        # Sử dụng placement_coords đã được Topology chuẩn bị sẵn
        possible_coords = [p for p in path_info.placement_coords if p != path_info.start_pos and p != path_info.target_pos]
        
        selected_coords = random.sample(possible_coords, min(item_count, len(possible_coords)))
        items = [{"type": item_type, "pos": pos} for pos in selected_coords]

        return {
            "start_pos": path_info.start_pos,
            "target_pos": path_info.target_pos,
            "items": items,
            "obstacles": path_info.obstacles
        }