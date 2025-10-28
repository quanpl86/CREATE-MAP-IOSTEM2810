import random
from .base_placer import BasePlacer
from src.map_generator.models.path_info import PathInfo

class EFShapePlacer(BasePlacer):
    """
    Đặt các vật phẩm cho các map có dạng chữ E hoặc F.
    Placer này đặt các vật phẩm trên tất cả các phần của hình dạng,
    khuyến khích người chơi sử dụng hàm hoặc vòng lặp lồng nhau.
    """

    def place_items(self, path_info: PathInfo, params: dict) -> dict:
        """
        Nhận một con đường chữ E/F và đặt vật phẩm lên đó.

        Args:
            path_info (PathInfo): Thông tin đường đi từ EFShapeTopology.
            params (dict): Các tham số bổ sung (ví dụ: item_count, item_type).

        Returns:
            dict: Một dictionary chứa layout map hoàn chỉnh.
        """
        print("    LOG: Placing items with 'ef_shape' logic...")

        item_count = params.get('item_count', 7)
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