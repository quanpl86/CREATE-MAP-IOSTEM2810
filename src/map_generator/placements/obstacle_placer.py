# src/map_generator/placements/obstacle_placer.py

import random
from .base_placer import BasePlacer
from src.map_generator.models.path_info import PathInfo

class ObstaclePlacer(BasePlacer):
    """
    Placer chuyên để đặt các chướng ngại vật (tường) lên đường đi,
    yêu cầu người chơi phải sử dụng lệnh 'jump'.
    Có thể kết hợp đặt thêm các vật phẩm và công tắc.
    """

    def place_items(self, path_info: PathInfo, params: dict) -> dict:
        """
        Đặt các vật phẩm, công tắc và quan trọng nhất là các chướng ngại vật.

        Args:
            path_info (PathInfo): Thông tin đường đi từ Topology.
            params (dict): Các tham số điều khiển việc đặt đối tượng.
                - obstacle_count (int): Số lượng vật cản cần đặt.
                - items_to_place (list): Danh sách các loại vật phẩm cần đặt (vd: ["crystal", "switch"]).

        Returns:
            dict: Layout map hoàn chỉnh.
        """
        print("    LOG: Placing items and obstacles with 'obstacle' logic...")

        items = []
        # [SỬA LỖI] Kế thừa danh sách chướng ngại vật từ Topology trước.
        obstacles = path_info.obstacles.copy()

        # [SỬA LỖI] Chỉ đặt vật cản trên các "đảo" (placement_coords), không đặt trên cầu.
        # Điều này ngăn việc vật cản chặn hoàn toàn đường đi.
        coords_for_obstacles = path_info.placement_coords if path_info.placement_coords else path_info.path_coords
        
        possible_coords = [p for p in coords_for_obstacles if p != path_info.start_pos and p != path_info.target_pos]
        random.shuffle(possible_coords)

        # 1. [CẢI TIẾN] Đặt chướng ngại vật, hỗ trợ cả 'obstacle_count' và 'obstacle_chance'
        obstacle_chance = params.get('obstacle_chance')
        if obstacle_chance is not None:
            # Nếu có 'obstacle_chance', đặt vật cản dựa trên xác suất
            coords_after_obstacles = []
            for pos in possible_coords:
                if random.random() < obstacle_chance:
                    obstacles.append({"type": "obstacle", "modelKey": "wall.brick01", "pos": pos})
                else:
                    coords_after_obstacles.append(pos)
            possible_coords = coords_after_obstacles # Cập nhật lại các vị trí còn trống
        else:
            # Nếu không, dùng logic 'obstacle_count' cũ
            num_obstacles = params.get('obstacle_count', 0)
            for _ in range(min(num_obstacles, len(possible_coords))):
                pos = possible_coords.pop(0)
                obstacles.append({"type": "obstacle", "modelKey": "wall.brick01", "pos": pos})

        # 2. [MỞ RỘNG] Đặt các vật phẩm và công tắc khác vào các vị trí còn lại
        # [CHUẨN HÓA] Chỉ sử dụng chuẩn 'items_to_place'
        items_to_place = params.get('items_to_place', []) # Cách mới, linh hoạt

        for item_type in items_to_place:
            if not possible_coords:
                print(f"    ⚠️ Cảnh báo: Không còn vị trí trống để đặt '{item_type}'.")
                break
            pos = possible_coords.pop(0)
            items.append({"type": item_type, "pos": pos})

        return {
            "start_pos": path_info.start_pos,
            "target_pos": path_info.target_pos,
            "items": items,
            "obstacles": obstacles
        }
