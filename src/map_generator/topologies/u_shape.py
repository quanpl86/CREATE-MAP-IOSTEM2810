# src/map_generator/topologies/u_shape.py

import random
from .base_topology import BaseTopology
from src.map_generator.models.path_info import PathInfo, Coord
from src.utils.geometry import add_vectors, FORWARD_X, FORWARD_Z, BACKWARD_X, BACKWARD_Z

class UShapeTopology(BaseTopology):
    """
    Tạo ra một con đường hình chữ U trên mặt phẳng 2D.
    Lý tưởng cho các bài học về tuần tự lệnh có hai lần rẽ cùng chiều.
    """

    def generate_path_info(self, grid_size: tuple, params: dict) -> PathInfo:
        print("    LOG: Generating 'u_shape' topology...")

        side_legs_len = params.get('side_legs_length', random.randint(3, 4))
        base_leg_len = params.get('base_leg_length', random.randint(3, 4))

        # Đảm bảo hình dạng nằm gọn trong map
        max_dim_x = grid_size[0] - 2
        max_dim_z = grid_size[2] - 2
        if side_legs_len > max_dim_z or base_leg_len > max_dim_x:
            side_legs_len = min(side_legs_len, max_dim_z - 1)
            base_leg_len = min(base_leg_len, max_dim_x - 1)

        # Chọn vị trí bắt đầu và hướng đi ngẫu nhiên
        start_x = random.randint(1, grid_size[0] - base_leg_len - 2)
        start_z = random.randint(1, grid_size[2] - side_legs_len - 2)
        y = 0
        start_pos: Coord = (start_x, y, start_z)

        # Cố định hướng để đơn giản: đi theo +Z, rồi +X, rồi -Z
        # Phiên bản nâng cao có thể ngẫu nhiên hóa các hướng này
        dir1 = FORWARD_Z
        dir2 = FORWARD_X
        dir3 = BACKWARD_Z

        path_coords: list[Coord] = []
        current_pos = start_pos

        # Vẽ cạnh 1
        for _ in range(side_legs_len):
            current_pos = add_vectors(current_pos, dir1)
            path_coords.append(current_pos)

        # Vẽ cạnh 2 (cạnh đáy)
        for _ in range(base_leg_len):
            current_pos = add_vectors(current_pos, dir2)
            path_coords.append(current_pos)

        # Vẽ cạnh 3
        for _ in range(side_legs_len):
            current_pos = add_vectors(current_pos, dir3)
            path_coords.append(current_pos)

        target_pos = path_coords[-1]

        return PathInfo(
            start_pos=start_pos,
            target_pos=target_pos,
            path_coords=path_coords
        )