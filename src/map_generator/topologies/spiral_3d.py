# src/map_generator/topologies/spiral_3d.py

import random
from .base_topology import BaseTopology
from src.map_generator.models.path_info import PathInfo, Coord
from src.utils.geometry import add_vectors, FORWARD_X, FORWARD_Z, BACKWARD_X, BACKWARD_Z, UP_Y, DOWN_Y

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
                - reverse (bool): True để tạo xoắn ốc đi từ trên xuống và thu hẹp dần.
                                   Ví dụ: 8 turns = 2 tầng.

        Returns:
            PathInfo: Một đối tượng chứa thông tin về con đường.
        """
        print("    LOG: Generating 'spiral_3d' topology...")

        num_turns = params.get('num_turns', 12) # Mặc định 12 lần rẽ = 3 tầng
        reverse = params.get('reverse', False) # Tham số mới để điều khiển hướng
        
        # Ước tính kích thước để đặt xoắn ốc vào giữa map
        max_len = (num_turns // 2) + 1
        start_x = grid_size[0] // 2
        start_z = grid_size[2] // 2
        y = 0

        path_coords: list[Coord] = []
        obstacles: list[dict] = []

        if not reverse:
            # --- LOGIC GỐC: Đi từ dưới lên, mở rộng ra ---
            start_pos: Coord = (start_x, y, start_z)
            path_coords.append(start_pos)
            current_pos = start_pos
            directions = [FORWARD_X, FORWARD_Z, BACKWARD_X, BACKWARD_Z]
            side_length = 1

            for i in range(num_turns):
                if i > 0 and i % 2 == 0:
                    side_length += 1
                
                move_direction = directions[i % 4]
                
                for _ in range(side_length):
                    current_pos = add_vectors(current_pos, move_direction)
                    path_coords.append(current_pos)
                
                if i < num_turns - 1:
                    stair_base_pos = add_vectors(current_pos, move_direction)
                    landing_pos = add_vectors(stair_base_pos, UP_Y)
                    obstacles.append({"type": "obstacle", "pos": stair_base_pos})
                    path_coords.append(landing_pos)
                    current_pos = landing_pos
        else:
            # --- LOGIC MỚI: Đi từ trên xuống, thu hẹp vào ---
            print("    LOG: Generating REVERSED spiral (top-down, shrinking)...")
            y = num_turns # Bắt đầu từ độ cao tối đa
            side_length = (num_turns // 2) + 1
            
            # Tính toán điểm bắt đầu ở góc ngoài cùng
            start_pos_calc = [start_x, y, start_z]
            for i in range(num_turns):
                if i > 0 and i % 2 == 0:
                    side_length -= 1
                move_direction = [FORWARD_X, FORWARD_Z, BACKWARD_X, BACKWARD_Z][i % 4]
                for _ in range(side_length):
                    start_pos_calc[0] -= move_direction[0]
                    start_pos_calc[2] -= move_direction[2]
            
            start_pos = tuple(start_pos_calc)
            path_coords.append(start_pos)
            current_pos = start_pos
            
            # Logic tạo đường đi ngược
            directions = [BACKWARD_X, BACKWARD_Z, FORWARD_X, FORWARD_Z] # Hướng ngược lại
            side_length = (num_turns // 2) + 1

            for i in range(num_turns):
                move_direction = directions[i % 4]
                
                for _ in range(side_length):
                    current_pos = add_vectors(current_pos, move_direction)
                    path_coords.append(current_pos)
                
                if i < num_turns - 1:
                    # Tạo bậc thang đi xuống
                    # Đối với đi xuống, không cần "bệ đỡ", chỉ cần đảm bảo có nền ở dưới
                    # và không gian đáp trống. gameSolver sẽ xử lý.
                    landing_pos = add_vectors(add_vectors(current_pos, move_direction), DOWN_Y)
                    path_coords.append(landing_pos)
                    current_pos = landing_pos

                if i > 0 and i % 2 != 0:
                    side_length -= 1

        target_pos = path_coords[-1]

        return PathInfo(
            start_pos=start_pos,
            target_pos=target_pos,
            path_coords=list(dict.fromkeys(path_coords)),
            placement_coords=path_coords, # Vẫn cần nền cho toàn bộ đường đi
            obstacles=obstacles # [MỚI] Trả về các khối bậc thang
        )