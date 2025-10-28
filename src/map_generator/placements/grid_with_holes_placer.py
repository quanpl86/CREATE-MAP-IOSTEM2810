import random
from .base_placer import BasePlacer
from src.map_generator.models.path_info import PathInfo

class GridWithHolesPlacer(BasePlacer):
    """
    Đặt các vật phẩm lên một map dạng lưới có hố.
    Placer này được thiết kế để hoạt động với GridWithHolesTopology.
    """

    def place_items(self, path_info: PathInfo, params: dict) -> dict:
        """
        Nhận một lưới có hố và rải các vật phẩm lên các ô đi được.

        Args:
            path_info (PathInfo): Thông tin từ GridWithHolesTopology.
            params (dict): Các tham số bổ sung.
                - item_count (int): Số lượng vật phẩm cần đặt.
                - item_type (str): Loại vật phẩm (ví dụ: 'crystal').

        Returns:
            dict: Một dictionary chứa layout map hoàn chỉnh.
        """
        print("    LOG: Placing items with 'grid_with_holes' logic...")

        item_count = params.get('item_count', 5)
        item_type = params.get('item_type', 'crystal')

        # Lấy các vị trí có thể đặt (các ô đi được, trừ điểm đầu và cuối)
        possible_coords = [p for p in path_info.path_coords if p != path_info.start_pos and p != path_info.target_pos]
        
        selected_coords = random.sample(possible_coords, min(item_count, len(possible_coords)))
        items = [{"type": item_type, "pos": pos} for pos in selected_coords]

        return {
            "start_pos": path_info.start_pos,
            "target_pos": path_info.target_pos,
            "items": items,
            "obstacles": path_info.obstacles # Lấy các hố đã được tạo bởi Topology
        }