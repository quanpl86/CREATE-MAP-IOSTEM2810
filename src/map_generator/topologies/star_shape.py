import random
from .base_topology import BaseTopology
from src.map_generator.models.path_info import PathInfo, Coord
from src.utils.geometry import add_vectors, FORWARD_X, FORWARD_Z, BACKWARD_X, BACKWARD_Z

class StarShapeTopology(BaseTopology):
    """
    Tạo ra một đường đi liên tục theo đường viền của một ngôi sao 5 cánh (pixel art).
    Đường đi được thiết kế để có Eulerian Path, cho phép robot di chuyển hết toàn bộ map.
    """

    def generate_path_info(self, grid_size: tuple, params: dict) -> PathInfo:
        print("    LOG: Generating 'star_shape' (outline) topology...")
        size = params.get('star_size', 3)  # Kích thước mỗi đoạn của ngôi sao
        if size < 2: size = 2

        center_x = grid_size[0] // 2
        center_z = grid_size[2] // 2

        # Tạo đường viền ngôi sao 5 cánh kiểu pixel (đi vòng ngoài)
        current_pos = (center_x, 0, center_z - size * 2)  # Bắt đầu từ đỉnh trên
        path_coords = [current_pos]

        # Ánh xạ hướng chuỗi sang vector
        direction_map = {
            'right': FORWARD_X,
            'down': FORWARD_Z,
            'left': BACKWARD_X,
            'up': BACKWARD_Z,
        }

        # Danh sách các đoạn di chuyển (hướng, số bước) để vẽ viền ngôi sao
        segments = [
            ('right', size),     # Đi đến đỉnh trên-phải
            ('down', size),      # Đi xuống cánh phải
            ('left', size),      # Đi vào trong
            ('down', size),      # Đi xuống đỉnh dưới-phải
            ('left', size),      # Đi qua đỉnh dưới
            ('up', size),        # Đi lên đỉnh dưới-trái
            ('left', size),      # Đi ra cánh trái
            ('up', size),        # Đi lên đỉnh trên-trái
            ('right', size),     # Đi vào trong
            ('up', size - 1),    # Đi lên gần đỉnh trên để nối vòng lặp
        ]

        for direction_key, steps in segments:
            move_vector = direction_map[direction_key]
            for _ in range(steps):
                current_pos = add_vectors(current_pos, move_vector)
                path_coords.append(current_pos)

        # Loại bỏ các điểm trùng lặp nhưng vẫn giữ nguyên thứ tự
        unique_path = list(dict.fromkeys(path_coords))

        return PathInfo(
            start_pos=unique_path[0],
            target_pos=unique_path[-1],
            path_coords=unique_path,
            placement_coords=unique_path
        )