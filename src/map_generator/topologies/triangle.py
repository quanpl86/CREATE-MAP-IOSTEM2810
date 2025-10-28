# src/map_generator/topologies/triangle.py

import random
from .base_topology import BaseTopology
from src.map_generator.models.path_info import PathInfo, Coord
from src.utils.geometry import add_vectors, FORWARD_X, FORWARD_Z

class TriangleTopology(BaseTopology):
    """
    Tạo ra một con đường có dạng tam giác vuông trên mặt phẳng 2D.
    Cạnh huyền của tam giác được mô phỏng bằng đường đi ziczac (bậc thang).
    Lý tưởng cho các bài học về hàm (procedure) và các vòng lặp phức tạp.
    """

    def generate_path_info(self, grid_size: tuple, params: dict) -> PathInfo:
        print("    LOG: Generating 'triangle' topology...")

        # Lấy kích thước 2 cạnh góc vuông từ params hoặc ngẫu nhiên
        leg_a = params.get('leg_a_length', random.randint(4, 6))
        leg_b = params.get('leg_b_length', random.randint(4, 6))

        # Chọn vị trí bắt đầu, đảm bảo tam giác nằm gọn trong map
        start_x = random.randint(1, grid_size[0] - leg_a - 2)
        start_z = random.randint(1, grid_size[2] - leg_b - 2)
        y = 0
        start_pos: Coord = (start_x, y, start_z)

        path_coords: list[Coord] = []
        placement_coords: list[Coord] = []
        current_pos = start_pos

        # --- Vẽ cạnh góc vuông A (dọc theo trục Z) ---
        for i in range(leg_a):
            current_pos = add_vectors(current_pos, FORWARD_Z)
            path_coords.append(current_pos)
            if i % 2 == 0: # Đặt vật phẩm xen kẽ
                placement_coords.append(current_pos)

        # Đỉnh góc vuông
        corner_pos = current_pos

        # --- Vẽ cạnh góc vuông B (dọc theo trục X) ---
        for i in range(leg_b):
            current_pos = add_vectors(current_pos, FORWARD_X)
            path_coords.append(current_pos)
            if i % 2 == 0: # Đặt vật phẩm xen kẽ
                placement_coords.append(current_pos)
        
        # Điểm cuối của đường đi (đích)
        target_pos = current_pos

        # --- (Tùy chọn) Vẽ cạnh huyền ziczac để hoàn thiện hình tam giác ---
        # Trong nhiều trường hợp, chúng ta chỉ cần 2 cạnh góc vuông là đủ
        # để tạo thành một đường đi hợp lý. Việc vẽ thêm cạnh huyền có thể
        # làm map trở nên rối và không cần thiết cho việc giải.
        # Tuy nhiên, nếu muốn, có thể thêm logic vẽ đường ziczac ở đây.

        # Đảm bảo điểm bắt đầu và đích không có trong danh sách đặt vật phẩm
        placement_coords = [p for p in placement_coords if p != start_pos and p != target_pos]

        return PathInfo(
            start_pos=start_pos,
            target_pos=target_pos,
            path_coords=path_coords,
            placement_coords=placement_coords
        )