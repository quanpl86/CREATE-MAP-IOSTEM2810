# src/map_generator/placements/swift_playground_placer.py
from .base_placer import BasePlacer
from src.map_generator.models.path_info import PathInfo
import random


class SwiftPlaygroundPlacer(BasePlacer):
    def place_items(self, path_info: PathInfo, params: dict) -> dict:
        """
        Đặt vật phẩm một cách chiến lược trên các "sàn" của mê cung nhiều tầng.
        Nó sẽ bỏ qua các bậc thang (obstacles) để đảm bảo vật phẩm chỉ nằm ở
        các khu vực bằng phẳng.
        """
        print("    LOG: Placing items with 'swift_playground_placer' logic...")
        items = []
        obstacles = path_info.obstacles.copy()
        items_to_place = params.get('items_to_place', ['crystal'] * 3) # Mặc định đặt 3 crystal

        # Lấy tọa độ của các bậc thang từ danh sách obstacles
        stair_coords = {tuple(obs['pos']) for obs in obstacles}

        # Các vị trí có thể đặt là các khối trên sàn (placement_coords)
        # nhưng không phải là bậc thang và không trùng với điểm đầu/cuối.
        possible_coords = [p for p in path_info.placement_coords if p not in stair_coords
                           and p != path_info.start_pos and p != path_info.target_pos]
        
        if possible_coords:
            # Chọn ngẫu nhiên các vị trí để đặt item
            num_to_place = min(len(items_to_place), len(possible_coords))
            selected_coords = random.sample(possible_coords, num_to_place)
            
            for i in range(num_to_place):
                item_type = items_to_place[i]
                # [CẢI TIẾN] Xử lý trường hợp 'gem' hoặc các loại item khác
                if item_type == "gem":
                    items.append({"type": "gem", "pos": selected_coords[i]})
                else: # Mặc định là crystal
                    items.append({"type": "crystal", "pos": selected_coords[i]})

        return {
            "start_pos": path_info.start_pos,
            "target_pos": path_info.target_pos,
            "items": items,
            "obstacles": obstacles
        }