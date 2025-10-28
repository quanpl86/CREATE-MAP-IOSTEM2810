# src/map_generator/topologies/l_shape.py

import random
from .base_topology import BaseTopology
from src.map_generator.models.path_info import PathInfo, Coord
from src.utils.geometry import add_vectors, FORWARD_X, FORWARD_Z, BACKWARD_X, BACKWARD_Z

class LShapeTopology(BaseTopology):
    """
    Tạo ra một con đường hình chữ L trên mặt phẳng 2D.
    Lý tưởng cho các bài học về tuần tự lệnh cơ bản có một lần rẽ.
    """

    def generate_path_info(self, grid_size: tuple, params: dict) -> PathInfo:
        """
        Tạo ra một đường đi hình chữ L với độ dài các cạnh và hướng ngẫu nhiên.

        Args:
            params (dict):
                - leg1_length (int): Độ dài cạnh thứ nhất.
                - leg2_length (int): Độ dài cạnh thứ hai.
                - orientation (str, optional): Hướng của chữ L. Ví dụ: "X_Z", "X_nZ", "Z_X", "nZ_X". Nếu không có, sẽ chọn ngẫu nhiên.

        Returns:
            PathInfo: Một đối tượng chứa thông tin về đường đi.
        """
        print("    LOG: Generating 'l_shape' topology...")

        # Lấy độ dài các cạnh từ params, hoặc dùng giá trị ngẫu nhiên
        leg1_len = params.get('leg1_length', random.randint(3, 5))
        leg2_len = params.get('leg2_length', random.randint(3, 5))

        # Đảm bảo hình dạng nằm gọn trong map
        max_dim = min(grid_size[0], grid_size[2]) - 2
        if leg1_len + 1 > max_dim or leg2_len + 1 > max_dim:
            leg1_len = min(leg1_len, max_dim - 2)
            leg2_len = min(leg2_len, max_dim - 2)

        # Chọn vị trí bắt đầu và hướng đi ngẫu nhiên
        start_x = random.randint(1, grid_size[0] - leg1_len - 2)
        start_z = random.randint(1, grid_size[2] - leg2_len - 2)
        y = 0
        start_pos: Coord = (start_x, y, start_z)

        # [CẢI TIẾN] Đọc hướng từ params hoặc chọn ngẫu nhiên
        orientation = params.get('orientation')
        
        all_orientations = {
            "X_Z": (FORWARD_X, FORWARD_Z),   # Đi theo +X, rồi +Z
            "X_nZ": (FORWARD_X, BACKWARD_Z), # Đi theo +X, rồi -Z
            "nX_Z": (BACKWARD_X, FORWARD_Z),  # Đi theo -X, rồi +Z
            "nX_nZ": (BACKWARD_X, BACKWARD_Z),# Đi theo -X, rồi -Z
            "Z_X": (FORWARD_Z, FORWARD_X),   # Đi theo +Z, rồi +X
            "Z_nX": (FORWARD_Z, BACKWARD_X),  # Đi theo +Z, rồi -X
            "nZ_X": (BACKWARD_Z, FORWARD_X),   # Đi theo -Z, rồi +X
            "nZ_nX": (BACKWARD_Z, BACKWARD_X) # Đi theo -Z, rồi -X
        }

        if orientation and orientation in all_orientations:
            dir1, dir2 = all_orientations[orientation]
        else:
            # Logic ngẫu nhiên cũ nếu không có tham số orientation
            directions = [random.choice([FORWARD_X, BACKWARD_X]), random.choice([FORWARD_Z, BACKWARD_Z])]
            random.shuffle(directions)
            dir1, dir2 = directions

        path_coords: list[Coord] = []
        current_pos = start_pos

        # Vẽ cạnh thứ nhất
        for _ in range(leg1_len):
            current_pos = add_vectors(current_pos, dir1)
            path_coords.append(current_pos)

        # Vẽ cạnh thứ hai
        for _ in range(leg2_len):
            current_pos = add_vectors(current_pos, dir2)
            path_coords.append(current_pos)

        target_pos = path_coords[-1]

        return PathInfo(
            start_pos=start_pos,
            target_pos=target_pos,
            path_coords=path_coords
        )