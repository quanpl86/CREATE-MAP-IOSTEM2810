# src/map_generator/topologies/plus_shape_islands.py

import random
from .base_topology import BaseTopology
from src.map_generator.models.path_info import PathInfo, Coord
from src.utils.geometry import add_vectors, scale_vector

class PlusShapeIslandsTopology(BaseTopology):
    """
    Tạo ra một cấu trúc gồm 4 hòn đảo được sắp xếp theo hình dấu cộng,
    hội tụ tại một điểm trung tâm.

    Lý tưởng cho các bài học về hàm có tham số hoặc cấu trúc điều kiện phức tạp,
    khi người chơi phải xử lý các nhánh khác nhau nhưng có cấu trúc tương tự.
    """

    def _create_island_pattern(self, top_left_corner: Coord) -> list[Coord]:
        """
        Tạo một mẫu đảo hình chữ U nhỏ.
        """
        x, y, z = top_left_corner
        return [(x, y, z), (x + 1, y, z), (x + 1, y, z + 1), (x, y, z + 1)]

    def generate_path_info(self, grid_size: tuple, params: dict) -> PathInfo:
        """
        Tạo ra 4 hòn đảo hình dấu cộng.

        Args:
            params (dict):
                - arm_length (int): Khoảng cách từ tâm đến mỗi đảo.

        Returns:
            PathInfo: Một đối tượng chứa thông tin về đường đi.
        """
        print("    LOG: Generating 'plus_shape_islands' topology...")

        island_size = (2, 2) # Kích thước của mẫu đảo U-shape

        # [SỬA LỖI] Giới hạn arm_length để đảm bảo nó không quá lớn so với grid_size
        # Chiều rộng/sâu tối thiểu cần thiết là 2 * arm_length + island_size + lề
        max_arm_length_x = (grid_size[0] - island_size[0] - 4) // 2
        max_arm_length_z = (grid_size[2] - island_size[1] - 4) // 2
        max_arm_length = min(max_arm_length_x, max_arm_length_z)

        arm_length_param = params.get('arm_length', random.randint(3, max_arm_length))
        arm_length = min(arm_length_param, max_arm_length) # Đảm bảo không vượt quá giới hạn

        # Chọn vị trí tâm an toàn để các cánh không bị vướng
        center_x = random.randint(arm_length + island_size[0], grid_size[0] - arm_length - island_size[0] - 2)
        center_z = random.randint(arm_length + island_size[1], grid_size[2] - arm_length - island_size[1] - 2)
        y = 0
        center_pos: Coord = (center_x, y, center_z)

        all_path_coords: list[Coord] = [center_pos]
        island_placement_coords: list[Coord] = []
        
        # Các hướng của 4 cánh (Đông, Tây, Nam, Bắc)
        directions = [(1, 0, 0), (-1, 0, 0), (0, 0, 1), (0, 0, -1)]
        island_starts = []

        # 1. Tạo 4 đảo và các cây cầu nối vào tâm
        for direction in directions:
            # Tính vị trí bắt đầu của đảo
            island_start_pos = add_vectors(center_pos, scale_vector(direction, arm_length))
            island_starts.append(island_start_pos)

            # Tạo đảo
            island_path = self._create_island_pattern(island_start_pos)
            island_placement_coords.extend(island_path)

            # Tạo cầu nối từ đảo về tâm
            # Ví dụ: đi từ (center_x + arm_length, y, center_z) về (center_x, y, center_z)
            current_bridge_pos = island_start_pos
            for _ in range(arm_length):
                # Di chuyển ngược hướng để về tâm
                move_back = scale_vector(direction, -1)
                current_bridge_pos = add_vectors(current_bridge_pos, move_back)
                if current_bridge_pos not in all_path_coords:
                    all_path_coords.append(current_bridge_pos)

        # 2. Chọn điểm bắt đầu và kết thúc ngẫu nhiên từ 4 đảo
        random.shuffle(island_starts)
        start_pos = island_starts.pop()
        target_pos = island_starts.pop()

        # 3. Nối tất cả các đường đi lại với nhau
        # all_path_coords đã chứa các cây cầu và tâm
        # island_placement_coords chứa các đảo
        # Kết hợp chúng lại
        full_path = list(dict.fromkeys(all_path_coords + island_placement_coords))

        return PathInfo(
            start_pos=start_pos,
            target_pos=target_pos,
            path_coords=full_path,
            placement_coords=island_placement_coords
        )