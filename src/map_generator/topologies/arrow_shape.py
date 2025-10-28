import random
from .base_topology import BaseTopology
from src.map_generator.models.path_info import PathInfo, Coord
from src.utils.geometry import add_vectors, FORWARD_Z

class ArrowShapeTopology(BaseTopology):
    """
    Tạo ra một con đường hình mũi tên trên mặt phẳng 2D.
    Bao gồm một "thân" thẳng và một "đầu" hình tam giác.
    Lý tưởng cho các bài tập tổng hợp, yêu cầu một chuỗi hành động phức tạp.
    """

    def generate_path_info(self, grid_size: tuple, params: dict) -> PathInfo:
        """
        Tạo ra một đường đi hình mũi tên.

        Args:
            params (dict):
                - shaft_length (int): Độ dài của thân mũi tên.
                - head_size (int): Kích thước của đầu mũi tên (quyết định chiều rộng và cao).

        Returns:
            PathInfo: Một đối tượng chứa thông tin về đường đi.
        """
        print("    LOG: Generating 'arrow_shape' topology...")

        # Lấy các tham số hoặc dùng giá trị ngẫu nhiên
        shaft_len = params.get('shaft_length', random.randint(3, 5))
        head_size = params.get('head_size', random.randint(2, 3)) # head_size=2 tạo ra đầu rộng 5, cao 2

        # Đảm bảo hình dạng nằm gọn trong map
        required_width = head_size * 2 + 1
        required_depth = shaft_len + head_size

        start_x = random.randint(head_size + 1, grid_size[0] - head_size - 2)
        start_z = random.randint(1, grid_size[2] - required_depth - 2)
        y = 0

        # Điểm bắt đầu của người chơi (ở đáy của thân)
        start_pos: Coord = (start_x, y, start_z)

        path_coords: list[Coord] = [] # Đường đi liên tục cho solver
        placement_coords: list[Coord] = [] # Tất cả các ô tạo thành hình mũi tên

        # 1. Vẽ thân mũi tên (đi theo trục Z)
        current_pos = start_pos
        for _ in range(shaft_len):
            current_pos = add_vectors(current_pos, FORWARD_Z)
            path_coords.append(current_pos)
            placement_coords.append(current_pos)

        junction_pos = current_pos # Điểm nối giữa thân và đầu

        # 2. Vẽ đầu mũi tên (hình tam giác)
        # Đầu mũi tên sẽ có chiều cao là `head_size` và chiều rộng là `2*head_size + 1`
        for i in range(1, head_size + 1):
            # Vị trí Z của hàng hiện tại trong tam giác
            current_z_level = junction_pos[2] + i
            # Chiều rộng của hàng tam giác ở độ cao i
            row_width = head_size - i
            
            # Vẽ các ô của hàng tam giác
            center_x = junction_pos[0]
            for j in range(-row_width, row_width + 1):
                coord = (center_x + j, y, current_z_level)
                placement_coords.append(coord)
                # Thêm vào đường đi chính nếu nó nằm trên đường thẳng đến đích
                if j == 0:
                    path_coords.append(coord)

        # Đích là đỉnh của mũi tên
        target_pos = (junction_pos[0], y, junction_pos[2] + head_size)

        # Đảm bảo đích có trong path_coords
        if target_pos not in path_coords:
            path_coords.append(target_pos)

        return PathInfo(
            start_pos=start_pos,
            target_pos=target_pos,
            path_coords=list(dict.fromkeys(path_coords)),
            placement_coords=list(dict.fromkeys(placement_coords))
        )