# src/map_generator/topologies/spiral_3d.py

import random
from .base_topology import BaseTopology
from src.map_generator.models.path_info import PathInfo, Coord
from src.utils.geometry import add_vectors, FORWARD_X, FORWARD_Z, BACKWARD_X, BACKWARD_Z, UP_Y

class Spiral3DTopology(BaseTopology):
    """
    Tạo ra một con đường xoắn ốc 3D đi lên, giống như một cầu thang.
    Lý tưởng cho các bài học về vòng lặp với các biến thay đổi (độ dài cạnh tăng dần).
    """

    def generate_path_info(self, grid_size: tuple, params: dict) -> PathInfo:
        """
        Tạo ra một đường đi xoắn ốc đi lên.

        Args:
            params (dict):
                - num_turns (int): Số lần rẽ góc vuông (mỗi 4 lần rẽ tạo 1 tầng).
                                   Ví dụ: 8 turns = 2 tầng.

        Returns:
            PathInfo: Một đối tượng chứa thông tin về con đường.
        """
        print("    LOG: Generating 'spiral_3d' topology...")

        num_turns = params.get('num_turns', 12) # Mặc định 12 lần rẽ = 3 tầng
        
        # Ước tính kích thước để đặt xoắn ốc vào giữa map
        max_len = (num_turns // 2) + 1
        start_x = grid_size[0] // 2
        start_z = grid_size[2] // 2
        y = 0

        start_pos: Coord = (start_x, y, start_z)
        path_coords: list[Coord] = [start_pos]
        obstacles: list[dict] = [] # [MỚI] Thêm danh sách vật cản cho bậc thang
        current_pos = start_pos

        # [SỬA LỖI] Logic mới: Tạo xoắn ốc đi ra và đi lên tại mỗi góc
        
        # Các hướng di chuyển theo thứ tự: Phải, Xuống (Z+), Trái, Lên (Z-)
        directions = [FORWARD_X, FORWARD_Z, BACKWARD_X, BACKWARD_Z]
        
        # Độ dài của cạnh xoắn ốc, ban đầu là 1
        side_length = 1

        for i in range(num_turns):
            # Cứ sau 2 lần rẽ, độ dài của cạnh sẽ tăng lên 1
            if i > 0 and i % 2 == 0:
                side_length += 1
            
            # Lấy hướng di chuyển cho cạnh hiện tại
            move_direction = directions[i % 4]
            
            # 1. Đi theo cạnh ngang/dọc
            for _ in range(side_length):
                current_pos = add_vectors(current_pos, move_direction)
                path_coords.append(current_pos)
            
            # 2. Đi lên 1 bậc tại góc rẽ để tạo cầu thang
            # Bỏ qua bước đi lên cuối cùng để target_pos nằm trên mặt phẳng
            if i < num_turns - 1:
                current_pos = add_vectors(current_pos, UP_Y)
                # [MỚI] Khối đi lên này là một vật cản (bề mặt bậc thang)
                obstacles.append({"modelKey": "ground.checker", "pos": current_pos})
                path_coords.append(current_pos)

        target_pos = path_coords[-1]

        return PathInfo(
            start_pos=start_pos,
            target_pos=target_pos,
            path_coords=path_coords,
            placement_coords=path_coords, # Vẫn cần nền cho toàn bộ đường đi
            obstacles=obstacles # [MỚI] Trả về các khối bậc thang
        )