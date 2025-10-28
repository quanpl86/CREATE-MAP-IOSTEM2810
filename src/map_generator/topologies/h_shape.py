import random
from .base_topology import BaseTopology
from src.map_generator.models.path_info import PathInfo, Coord
from src.utils.geometry import add_vectors, FORWARD_X, FORWARD_Z, BACKWARD_Z, BACKWARD_X

class HShapeTopology(BaseTopology):
    """
    Tạo ra một con đường hình chữ H trên mặt phẳng 2D.
    Lý tưởng cho các bài học về hàm (function), nơi người chơi có thể
    viết một hàm để đi hết một "cột" và gọi lại nó.
    """

    def generate_path_info(self, grid_size: tuple, params: dict) -> PathInfo:
        """
        Tạo ra một đường đi hình chữ H.

        Args:
            params (dict):
                - column_length (int): Số lượng ô trong mỗi "cột" dọc.
                - column_spacing (int): Khoảng cách (số ô trống) giữa hai cột.
                - bar_position_offset (int): Vị trí của thanh ngang tính từ đáy cột (0-indexed).

        Returns:
            PathInfo: Một đối tượng chứa thông tin về đường đi.
        """
        print("    LOG: Generating 'h_shape' topology...")

        # --- PHẦN 1: LẤY VÀ KIỂM TRA THAM SỐ (Giữ nguyên phần lớn) ---
        column_len = params.get('column_length', random.randint(3, 5))
        column_spacing = params.get('column_spacing', random.randint(1, 3))
        # Đảm bảo thanh ngang không nằm ở ô trên cùng hoặc dưới cùng
        bar_offset = params.get('bar_position_offset', random.randint(1, column_len - 2))

        if column_len < 3: column_len = 3
        if column_spacing < 1: column_spacing = 1
        bar_offset = max(1, min(bar_offset, column_len - 2))

        required_width = 2 + column_spacing
        required_depth = column_len

        if required_width > grid_size[0] - 2:
            required_width = grid_size[0] - 2
            column_spacing = max(1, required_width - 2)
        
        if required_depth > grid_size[2] - 2:
            required_depth = grid_size[2] - 2
            column_len = max(3, required_depth)

        bar_offset = max(1, min(bar_offset, column_len - 2))

        start_x_h = random.randint(1, grid_size[0] - required_width - 1)
        start_z_h = random.randint(1, grid_size[2] - required_depth - 1)
        y = 0

        start_pos: Coord = (start_x_h, y, start_z_h)

        # --- PHẦN 2: TẠO HÌNH DẠNG (placement_coords) MỘT CÁCH RÕ RÀNG ---
        
        left_column_coords = []
        current_pos = start_pos
        for _ in range(column_len):
            left_column_coords.append(current_pos)
            current_pos = add_vectors(current_pos, FORWARD_Z)

        right_column_start_pos: Coord = (start_x_h + column_spacing + 1, y, start_z_h)
        right_column_coords = []
        current_pos = right_column_start_pos
        for _ in range(column_len):
            right_column_coords.append(current_pos)
            current_pos = add_vectors(current_pos, FORWARD_Z)

        # Thanh ngang bắt đầu từ cột trái, tại độ cao bar_offset
        bar_start_pos: Coord = (start_x_h, y, start_z_h + bar_offset)
        horizontal_bar_coords = []
        current_pos = bar_start_pos
        # Đi từ cột trái sang cột phải, bao gồm cả 2 ô ở 2 cột (column_spacing + 2 ô)
        for _ in range(column_spacing + 2):
            horizontal_bar_coords.append(current_pos)
            current_pos = add_vectors(current_pos, FORWARD_X)
            
        all_h_coords = left_column_coords + right_column_coords + horizontal_bar_coords
        placement_coords = list(dict.fromkeys(all_h_coords))

        # --- PHẦN 3: (SỬA LỖI) TẠO ĐƯỜNG ĐI (path_coords) ĐI QUA THANH NGANG ---

        path_coords: list[Coord] = [start_pos]
        current_path_pos = start_pos
        
        # 1. Đi từ dưới cột trái lên đến thanh ngang
        # bar_offset là chỉ số (0-indexed), nên cần đi bar_offset bước
        for _ in range(bar_offset):
            current_path_pos = add_vectors(current_path_pos, FORWARD_Z)
            path_coords.append(current_path_pos)
        
        # 2. Đi ngang qua thanh ngang để đến cột phải
        # Đi column_spacing bước trong khoảng trống + 1 bước để đến cột phải
        for _ in range(column_spacing + 1):
            current_path_pos = add_vectors(current_path_pos, FORWARD_X)
            path_coords.append(current_path_pos)
            
        # 3. Đi từ thanh ngang xuống đáy cột phải
        for _ in range(bar_offset):
            current_path_pos = add_vectors(current_path_pos, BACKWARD_Z)
            path_coords.append(current_path_pos)

        target_pos = current_path_pos

        return PathInfo(
            start_pos=start_pos,
            target_pos=target_pos,
            path_coords=path_coords,
            placement_coords=placement_coords
        )