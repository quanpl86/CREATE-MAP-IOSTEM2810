# src/map_generator/topologies/circle.py

import random
import math
from .base_topology import BaseTopology
from src.map_generator.models.path_info import PathInfo, Coord

class CircleTopology(BaseTopology):
    """
    Tạo ra một con đường hình tròn trên mặt phẳng 2D.
    """

    def generate_path_info(self, grid_size: tuple, params: dict) -> PathInfo:
        """
        Tạo ra một đường đi hình tròn.

        Args:
            params (dict):
                - radius (int): Bán kính của hình tròn.
                - num_points (int): Số lượng điểm để tạo thành hình tròn.

        Returns:
            PathInfo: Một đối tượng chứa thông tin về đường đi.
        """
        print("    LOG: Generating 'circle' topology...")

        radius = params.get('radius', 5)
        num_points = params.get('num_points', 16)

        # [FIX] Sửa lỗi randrange khi radius quá lớn so với grid_size
        center_x = random.randint(radius + 1, grid_size[0] - radius - 1)
        center_z = random.randint(radius + 1, grid_size[2] - radius - 1)
        y = 0

        path_coords: list[Coord] = []
        for i in range(num_points):
            angle = 2 * math.pi * i / num_points
            x = center_x + int(radius * math.cos(angle))
            z = center_z + int(radius * math.sin(angle))
            path_coords.append((x, y, z))

        # Loại bỏ các điểm trùng lặp và giữ nguyên thứ tự
        unique_coords = list(dict.fromkeys(path_coords))

        start_pos = unique_coords[0]
        target_pos = unique_coords[-1]

        return PathInfo(start_pos=start_pos, target_pos=target_pos, path_coords=unique_coords, placement_coords=unique_coords)