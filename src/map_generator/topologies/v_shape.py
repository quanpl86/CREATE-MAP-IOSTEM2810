import random
from .base_topology import BaseTopology
from src.map_generator.models.path_info import PathInfo, Coord
from src.utils.geometry import add_vectors, FORWARD_X, FORWARD_Z, BACKWARD_X

class VShapeTopology(BaseTopology):
    """
    Tạo ra một con đường hình chữ V trên mặt phẳng 2D.
    Lý tưởng cho các bài học về tuần tự hoặc hàm đơn giản.
    """

    def generate_path_info(self, grid_size: tuple, params: dict) -> PathInfo:
        """
        Tạo ra một đường đi hình chữ V.

        Args:
            params (dict):
                - arm_length (int): Số cặp bước đi trong mỗi nhánh chữ V.

        Returns:
            PathInfo: Một đối tượng chứa thông tin về đường đi.
        """
        print("    LOG: Generating 'v_shape' topology...")

        arm_len = params.get('arm_length', random.randint(3, 5))
        y = 0

        # [SỬA LỖI] Tính toán kích thước cần thiết dựa trên đường đi zigzag
        # Mỗi bước trong arm_len sẽ tạo ra 2 ô (1 ngang, 1 dọc)
        required_width = arm_len * 2
        required_depth = arm_len * 2
        
        # Đảm bảo nằm gọn trong map
        if required_width > grid_size[0] - 2: required_width = grid_size[0] - 2
        if required_depth > grid_size[2] - 2: required_depth = grid_size[2] - 2
        
        start_x = random.randint(1, grid_size[0] - required_width - 1)
        start_z = random.randint(1, grid_size[2] - required_depth - 1)

        start_pos: Coord = (start_x, y, start_z)
        # Sửa lỗi: Đường đi phải luôn bắt đầu bằng vị trí xuất phát
        path_coords: list[Coord] = [start_pos]
        current_pos = start_pos

        # [SỬA LỖI] Thay thế di chuyển chéo bằng di chuyển zigzag (bậc thang)
        
        # Nhánh đầu tiên của chữ V (đi tiến và sang phải)
        # Hướng di chuyển tổng thể: (+X, +Z)
        for _ in range(arm_len):
            # Bước 1: Đi tiến (trục Z)
            current_pos = add_vectors(current_pos, FORWARD_Z) # (0, 0, 1)
            path_coords.append(current_pos)
            # Bước 2: Đi sang phải (trục X)
            current_pos = add_vectors(current_pos, FORWARD_X) # (1, 0, 0)
            path_coords.append(current_pos)

        # Nhánh thứ hai của chữ V (đi tiến và sang trái)
        # Hướng di chuyển tổng thể: (-X, +Z)
        for _ in range(arm_len):
            # Bước 1: Đi tiến (trục Z)
            current_pos = add_vectors(current_pos, FORWARD_Z) # (0, 0, 1)
            path_coords.append(current_pos)
            # Bước 2: Đi sang trái (trục X)
            current_pos = add_vectors(current_pos, BACKWARD_X) # (-1, 0, 0)
            path_coords.append(current_pos)

        target_pos = path_coords[-1]

        # placement_coords chính là path_coords vì mỗi ô đi qua đều cần có đất
        return PathInfo(
            start_pos=start_pos,
            target_pos=target_pos,
            path_coords=path_coords,
            placement_coords=path_coords
        )