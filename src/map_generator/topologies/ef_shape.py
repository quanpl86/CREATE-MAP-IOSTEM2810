import random
from .base_topology import BaseTopology
from src.map_generator.models.path_info import PathInfo, Coord
from src.utils.geometry import add_vectors, FORWARD_X, FORWARD_Z, BACKWARD_X

class EFShapeTopology(BaseTopology):
    """
    Tạo ra một con đường hình chữ E hoặc F trên mặt phẳng 2D.
    Lý tưởng cho các bài học về vòng lặp lồng nhau hoặc hàm với tham số,
    ví dụ: một hàm `draw_branch(length)` có thể được gọi nhiều lần.
    """

    def generate_path_info(self, grid_size: tuple, params: dict) -> PathInfo:
        """
        Tạo ra một đường đi hình chữ E/F.

        Args:
            params (dict):
                - stem_length (int): Độ dài của "thân" chính.
                - num_branches (int): Số lượng nhánh (2 cho F, 3 cho E).
                - branch_length (int): Độ dài của mỗi nhánh.
                - branch_spacing (int): Khoảng cách (số ô) giữa các nhánh.

        Returns:
            PathInfo: Một đối tượng chứa thông tin về đường đi.
        """
        print("    LOG: Generating 'ef_shape' topology...")

        # Lấy các tham số hoặc dùng giá trị ngẫu nhiên
        stem_len = params.get('stem_length', random.randint(5, 7))
        num_branches = params.get('num_branches', random.choice([2, 3])) # 2 cho F, 3 cho E
        branch_len = params.get('branch_length', random.randint(2, 4))
        # Khoảng cách giữa các điểm bắt đầu của nhánh
        branch_spacing = params.get('branch_spacing', (stem_len - 1) // (num_branches - 1) if num_branches > 1 else 0)

        # Đảm bảo các tham số hợp lệ
        if stem_len < num_branches * 2 -1: stem_len = num_branches * 2 -1
        if branch_spacing * (num_branches - 1) >= stem_len: branch_spacing = (stem_len - 1) // (num_branches - 1)

        # Đảm bảo hình dạng nằm gọn trong map
        required_width = branch_len + 1
        required_depth = stem_len
        start_x = random.randint(1, grid_size[0] - required_width - 2)
        start_z = random.randint(1, grid_size[2] - required_depth - 2)
        y = 0

        # Điểm bắt đầu của người chơi (góc dưới của thân)
        start_pos: Coord = (start_x, y, start_z)

        path_coords: list[Coord] = [] # Đường đi liên tục cho solver
        placement_coords: list[Coord] = [] # Tất cả các ô tạo thành hình E/F

        # 1. Vẽ thân chính (đi theo trục Z)
        current_pos = start_pos
        stem_coords = [start_pos]
        for _ in range(stem_len - 1):
            current_pos = add_vectors(current_pos, FORWARD_Z)
            stem_coords.append(current_pos)
        
        placement_coords.extend(stem_coords)

        # 2. Vẽ các nhánh (đi theo trục X)
        for i in range(num_branches):
            # Điểm bắt đầu của nhánh nằm trên thân
            branch_start_z = start_z + i * branch_spacing
            # Đảm bảo nhánh cuối cùng nằm ở đỉnh của thân
            if i == num_branches - 1:
                branch_start_z = start_z + stem_len - 1
            
            branch_start_pos: Coord = (start_x, y, branch_start_z)
            
            temp_pos = branch_start_pos
            for _ in range(branch_len):
                temp_pos = add_vectors(temp_pos, FORWARD_X)
                placement_coords.append(temp_pos)

        # 3. Tạo đường đi liên tục cho solver
        # Đường đi sẽ là đi hết thân, sau đó đi vào và ra từng nhánh
        path_coords.extend(stem_coords) # Đi hết thân
        # Đi vào và ra nhánh cuối cùng
        last_branch_start = (start_x, y, start_z + stem_len - 1)
        temp_pos = last_branch_start
        for _ in range(branch_len):
            temp_pos = add_vectors(temp_pos, FORWARD_X)
            path_coords.append(temp_pos)

        target_pos = path_coords[-1] # Đích ở cuối nhánh trên cùng

        return PathInfo(
            start_pos=start_pos,
            target_pos=target_pos,
            path_coords=list(dict.fromkeys(path_coords)),
            placement_coords=list(dict.fromkeys(placement_coords))
        )