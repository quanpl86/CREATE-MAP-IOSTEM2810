import random
from .base_placer import BasePlacer
from src.map_generator.models.path_info import PathInfo
from src.utils.randomizer import shuffle_list

class RandomItemPlacer(BasePlacer):
    """
    Một Placer đơn giản, đặt các vật phẩm được yêu cầu vào các vị trí ngẫu nhiên
    trên các tọa độ đường đi (path_coords) có sẵn.
    """

    def place_items(self, path_info: PathInfo, params: dict) -> dict:
        """
        Đặt các vật phẩm một cách ngẫu nhiên.

        Args:
            path_info (PathInfo): Thông tin đường đi từ một lớp Topology.
            params (dict): Các tham số, có thể chứa 'items_to_place'.

        Returns:
            dict: Một dictionary chứa layout map hoàn chỉnh.
        """
        print("    LOG: Placing items with 'random_item_placement' logic...")

        items_to_place = params.get('items_to_place', [])
        if not isinstance(items_to_place, list):
            items_to_place = [items_to_place]

        # Lấy tất cả các vị trí có thể đặt (trừ điểm bắt đầu và kết thúc)
        possible_coords = [p for p in path_info.path_coords if p != path_info.start_pos and p != path_info.target_pos]
        selected_coords = shuffle_list(possible_coords)

        items = []
        for i in range(min(len(items_to_place), len(selected_coords))):
            item_type = items_to_place[i]
            pos = selected_coords[i]
            items.append({"type": item_type, "pos": pos})
            print(f"      -> Đã đặt '{item_type}' tại vị trí {pos}")

        return {"start_pos": path_info.start_pos, "target_pos": path_info.target_pos, "items": items, "obstacles": path_info.obstacles}