# src/map_generator/topologies/z_shape.py

import random
from .base_topology import BaseTopology
from src.map_generator.models.path_info import PathInfo, Coord
from src.utils.geometry import add_vectors, FORWARD_X, FORWARD_Z, BACKWARD_X

class ZShapeTopology(BaseTopology):
    """
    Tạo ra một con đường hình chữ Z trên mặt phẳng 2D.
    """

    def generate_path_info(self, grid_size: tuple, params: dict) -> PathInfo:
        """
        Tạo ra một đường đi hình chữ Z.

        Args:
            params (dict):
                - leg1_length (int): Độ dài cạnh ngang trên.
                - leg2_length (int): Số cặp bước đi của cạnh chéo.
                - leg3_length (int): Độ dài cạnh ngang dưới.

        Returns:
            PathInfo: Một đối tượng chứa thông tin về đường đi.
        """
        print("    LOG: Generating 'z_shape' topology...")

        leg1_len = params.get('leg1_length', random.randint(2, 4))
        leg2_len = params.get('leg2_length', random.randint(2, 4))
        leg3_len = params.get('leg3_length', random.randint(2, 4))
        y = 0

        # [SỬA LỖI] Cần tính toán không gian cần thiết một cách an toàn
        required_width = leg1_len + leg3_len
        required_depth = leg2_len + 1

        start_x = random.randint(1, grid_size[0] - required_width - 1)
        start_z = random.randint(1, grid_size[2] - required_depth - 1)
        
        start_pos: Coord = (start_x, y, start_z)
        # [SỬA LỖI] Luôn bắt đầu path_coords với vị trí xuất phát
        path_coords: list[Coord] = [start_pos]
        current_pos = start_pos

        # Cạnh ngang trên (đi sang phải)
        for _ in range(leg1_len):
            current_pos = add_vectors(current_pos, FORWARD_X)
            path_coords.append(current_pos)

        # [SỬA LỖI] Cạnh chéo: Thay thế bằng các bước đi zigzag
        # Hướng tổng thể: (-X, +Z)
        for _ in range(leg2_len):
            # Bước 1: Đi tiến (trục Z)
            current_pos = add_vectors(current_pos, FORWARD_Z)
            path_coords.append(current_pos)
            # Bước 2: Đi sang trái (trục X)
            current_pos = add_vectors(current_pos, BACKWARD_X)
            path_coords.append(current_pos)

        # Cạnh ngang dưới (đi sang phải)
        for _ in range(leg3_len):
            current_pos = add_vectors(current_pos, FORWARD_X)
            path_coords.append(current_pos)

        target_pos = path_coords[-1]

        return PathInfo(
            start_pos=start_pos,
            target_pos=target_pos,
            path_coords=path_coords,
            placement_coords=path_coords
        )