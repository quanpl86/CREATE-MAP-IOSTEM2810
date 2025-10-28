# src/map_generator/topologies/s_shape.py

import random
from .base_topology import BaseTopology
from src.map_generator.models.path_info import PathInfo, Coord
from src.utils.geometry import add_vectors, FORWARD_X, FORWARD_Z, BACKWARD_X, BACKWARD_Z

class SShapeTopology(BaseTopology):
    """
    Tạo ra một con đường hình chữ S trên mặt phẳng 2D.
    Lý tưởng cho các bài học về tuần tự lệnh có hai lần rẽ ngược chiều.
    """

    def generate_path_info(self, grid_size: tuple, params: dict) -> PathInfo:
        print("    LOG: Generating 's_shape' topology...")

        leg1_len = params.get('leg1_length', random.randint(2, 4))
        leg2_len = params.get('leg2_length', random.randint(3, 4))
        leg3_len = params.get('leg3_length', random.randint(2, 4))

        # Đảm bảo hình dạng nằm gọn trong map
        max_dim_x = grid_size[0] - 2
        max_dim_z = grid_size[2] - 2
        if leg1_len + leg3_len > max_dim_z or leg2_len > max_dim_x:
            leg1_len = min(leg1_len, max_dim_z // 2 -1)
            leg3_len = min(leg3_len, max_dim_z // 2 -1)
            leg2_len = min(leg2_len, max_dim_x - 1)

        # Chọn vị trí bắt đầu
        start_x = random.randint(1, grid_size[0] - leg2_len - 2)
        start_z = random.randint(1, grid_size[2] - (leg1_len + leg3_len) - 2)
        y = 0
        start_pos: Coord = (start_x, y, start_z)

        # Cố định hướng để đơn giản: đi theo +Z, rồi +X, rồi +Z
        dir1 = FORWARD_Z
        dir2 = FORWARD_X
        dir3 = FORWARD_Z

        path_coords: list[Coord] = []
        current_pos = start_pos

        # Vẽ cạnh 1
        for _ in range(leg1_len):
            current_pos = add_vectors(current_pos, dir1)
            path_coords.append(current_pos)

        # Vẽ cạnh 2
        for _ in range(leg2_len):
            current_pos = add_vectors(current_pos, dir2)
            path_coords.append(current_pos)

        # Vẽ cạnh 3
        for _ in range(leg3_len):
            current_pos = add_vectors(current_pos, dir3)
            path_coords.append(current_pos)

        target_pos = path_coords[-1]

        return PathInfo(
            start_pos=start_pos,
            target_pos=target_pos,
            path_coords=path_coords
        )