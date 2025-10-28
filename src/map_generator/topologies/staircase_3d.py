# src/map_generator/topologies/staircase_3d.py

import random
from .base_topology import BaseTopology
from src.map_generator.models.path_info import PathInfo, Coord
from src.utils.geometry import add_vectors

class Staircase3DTopology(BaseTopology):
    """
    Tạo ra một cấu trúc cầu thang 3D đi lên theo cả hai trục X và Z.
    Lý tưởng cho các bài học về vòng lặp và di chuyển trong không gian 3D.
    """

    def generate_path_info(self, grid_size: tuple, params: dict) -> PathInfo:
        """
        Tạo ra một cầu thang 3D.

        Args:
            params (dict):
                - num_steps (int): Số bậc thang.

        Returns:
            PathInfo: Một đối tượng chứa thông tin về cầu thang.
        """
        print("    LOG: Generating 'staircase_3d' topology...")

        num_steps = params.get('num_steps', 6)

        max_dim = min(grid_size[0], grid_size[1], grid_size[2]) - 2
        if num_steps >= max_dim:
            num_steps = max_dim - 1

        start_x = random.randint(1, grid_size[0] - num_steps - 2)
        start_z = random.randint(1, grid_size[2] - num_steps - 2)
        start_y = 0

        start_pos: Coord = (start_x, start_y, start_z)
        path_coords: list[Coord] = []
        current_pos = start_pos

        # Mỗi bậc thang sẽ đi tới 1 ô (trục Z) và đi lên 1 ô (trục Y)
        for i in range(num_steps):
            current_pos = add_vectors(current_pos, (0, 1, 1)) # dx=0, dy=1, dz=1
            path_coords.append(current_pos)

        target_pos = path_coords[-1]

        return PathInfo(start_pos=start_pos, target_pos=target_pos, path_coords=path_coords, placement_coords=path_coords)