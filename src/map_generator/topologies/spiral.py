# src/map_generator/topologies/spiral.py

import random
import math
from .base_topology import BaseTopology
from src.map_generator.models.path_info import PathInfo, Coord
from src.utils.geometry import add_vectors, FORWARD_X, FORWARD_Z, BACKWARD_X, BACKWARD_Z

class SpiralTopology(BaseTopology):
    """
    Tạo ra một con đường xoắn ốc 2D hình vuông trên mặt phẳng XZ.
    Lý tưởng cho các bài học về vòng lặp với các biến thay đổi (độ dài cạnh thay đổi).
    """

    def generate_path_info(self, grid_size: tuple, params: dict) -> PathInfo:
        """
        Tạo ra một đường đi xoắn ốc hình vuông, đi từ ngoài vào trong hoặc từ trong ra ngoài.

        Args:
            params (dict):
                - num_turns (int): Số lần rẽ góc vuông.
                - start_at_center (bool): True để bắt đầu từ tâm đi ra, False để đi từ ngoài vào.

        Returns:
            PathInfo: Một đối tượng chứa thông tin về con đường.
        """
        print("    LOG: Generating 'spiral' (2D) topology...")

        num_turns = params.get('num_turns', 8)
        start_at_center = params.get('start_at_center', False)

        # Tính toán kích thước tối đa của xoắn ốc để nó nằm gọn trong lưới
        max_side_len = math.ceil(num_turns / 2) + 1
        if max_side_len * 2 > min(grid_size[0], grid_size[2]) - 4:
            num_turns = min(num_turns, 6) # Giảm số vòng nếu quá lớn
            max_side_len = math.ceil(num_turns / 2) + 1

        # Đặt tâm của xoắn ốc vào giữa lưới
        center_x = grid_size[0] // 2
        center_z = grid_size[2] // 2
        y = 0

        # Tính toán điểm bắt đầu ở góc trên-trái của hình xoắn ốc
        start_x = center_x - max_side_len // 2
        start_z = center_z - max_side_len // 2

        # --- Logic tạo xoắn ốc từ ngoài vào trong ---
        current_pos: Coord = (start_x, y, start_z)
        path_coords: list[Coord] = [current_pos]

        # Các hướng di chuyển theo thứ tự: Phải (+X), Xuống (+Z), Trái (-X), Lên (-Z)
        directions = [FORWARD_X, FORWARD_Z, BACKWARD_X, BACKWARD_Z]
        
        # Độ dài các cạnh sẽ giảm dần
        side_length = max_side_len

        for i in range(num_turns):
            # Lấy hướng di chuyển cho cạnh hiện tại
            move_direction = directions[i % 4]
            
            # Cứ sau 1 lần rẽ, độ dài cạnh giảm đi 1
            if i > 0:
                side_length -=1

            # Vẽ một cạnh của xoắn ốc
            for _ in range(side_length):
                current_pos = add_vectors(current_pos, move_direction)
                path_coords.append(current_pos)

        # Loại bỏ các điểm trùng lặp có thể xảy ra ở tâm
        path_coords = list(dict.fromkeys(path_coords))

        # Nếu yêu cầu bắt đầu từ tâm, chúng ta chỉ cần đảo ngược lại danh sách tọa độ
        if start_at_center:
            path_coords.reverse()
        
        start_pos = path_coords[0]
        target_pos = path_coords[-1]

        return PathInfo(
            start_pos=start_pos,
            target_pos=target_pos,
            path_coords=path_coords,
            placement_coords=path_coords
        )
