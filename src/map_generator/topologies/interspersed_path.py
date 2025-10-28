# src/map_generator/topologies/interspersed_path.py

import random
from .base_topology import BaseTopology
from src.map_generator.models.path_info import PathInfo, Coord
from src.utils.geometry import add_vectors, FORWARD_X, FORWARD_Z, BACKWARD_X, BACKWARD_Z

class InterspersedPathTopology(BaseTopology):
    """
    [REWRITTEN] Tạo ra một con đường chính với các nhánh phụ rẽ ra hai bên.
    Lý tưởng cho các bài học về hàm, nơi mỗi nhánh có thể được giải quyết bằng một hàm con.
    """
    
    def generate_path_info(self, grid_size: tuple, params: dict) -> PathInfo:
        """
        Tạo ra một con đường thẳng với các nhánh phụ.

        Returns:
            PathInfo: Một đối tượng chứa thông tin về con đường phức tạp này.
        """
        print("    LOG: Generating 'interspersed_path' topology...")
        
        main_path_length = params.get('main_path_length', 9)
        num_branches = params.get('num_branches', 2)
        branch_length = params.get('branch_length', 2)
        
        # Đảm bảo đường đi và các nhánh nằm gọn trong map
        if main_path_length >= grid_size[0] - 4:
            main_path_length = grid_size[0] - 5
        if branch_length * 2 + 1 >= grid_size[2] - 2:
            branch_length = 1

        # Cố định trục chính là X, các nhánh rẽ theo trục Z để đơn giản hóa
        # Vị trí bắt đầu an toàn
        start_x = random.randint(1, grid_size[0] - main_path_length - 2)
        start_z = random.randint(branch_length + 1, grid_size[2] - branch_length - 2)
        y = 0
        start_pos: Coord = (start_x, y, start_z)
        
        # --- Logic tạo đường đi và các nhánh ---
        all_coords = {start_pos}
        current_pos = start_pos
        
        # Chọn các vị trí trên đường chính để rẽ nhánh
        branch_points_indices = sorted(random.sample(range(1, main_path_length - 1), min(num_branches, main_path_length - 2)))
        branch_point_set = set(branch_points_indices)
        
        # Hướng rẽ nhánh (lên hoặc xuống theo trục Z)
        branch_direction = FORWARD_Z

        # Vẽ đường đi chính và các nhánh
        for i in range(main_path_length):
            current_pos = add_vectors(current_pos, FORWARD_X)
            all_coords.add(current_pos)

            # Nếu đây là điểm rẽ nhánh
            if i + 1 in branch_point_set:
                branch_pos = current_pos
                # Vẽ một nhánh
                for _ in range(branch_length):
                    branch_pos = add_vectors(branch_pos, branch_direction)
                    all_coords.add(branch_pos)
                # Đảo hướng cho nhánh tiếp theo
                branch_direction = BACKWARD_Z if branch_direction == FORWARD_Z else FORWARD_Z

        target_pos = current_pos
        
        # path_coords và placement_coords là như nhau trong trường hợp này
        # vì tất cả các ô đều cần có đất
        final_coords = sorted(list(all_coords))

        return PathInfo(
            start_pos=start_pos,
            target_pos=target_pos,
            path_coords=final_coords,
            placement_coords=final_coords
        )