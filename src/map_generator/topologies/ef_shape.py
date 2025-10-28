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

        Returns:
            PathInfo: Một đối tượng chứa thông tin về đường đi.
        """
        print("    LOG: Generating 'ef_shape' topology...")

        # --- PHẦN 1: LẤY VÀ KIỂM TRA THAM SỐ (Tối ưu hóa) ---
        stem_len = params.get('stem_length', random.randint(5, 7))
        num_branches = params.get('num_branches', random.choice([2, 3])) # 2 cho F, 3 cho E
        branch_len = params.get('branch_length', random.randint(2, 4))
        
        # Đảm bảo stem_len đủ dài cho các nhánh
        min_stem_len = 3 if num_branches == 2 else 5 # F cần ít nhất 3 ô, E cần ít nhất 5
        if stem_len < min_stem_len: stem_len = min_stem_len

        # Đảm bảo hình dạng nằm gọn trong map
        required_width = branch_len + 1 # Thân + nhánh
        required_depth = stem_len
        
        # Điều chỉnh nếu cần
        if required_width > grid_size[0] - 2: required_width = grid_size[0] - 2
        if required_depth > grid_size[2] - 2: required_depth = grid_size[2] - 2
        
        start_x = random.randint(1, grid_size[0] - required_width - 1)
        start_z = random.randint(1, grid_size[2] - required_depth - 1)
        y = 0

        start_pos: Coord = (start_x, y, start_z)
        
        # --- PHẦN 2: TẠO HÌNH DẠNG (placement_coords) CHÍNH XÁC ---
        
        placement_coords = set()

        # 1. Vẽ thân chính (luôn tồn tại)
        for i in range(stem_len):
            placement_coords.add((start_x, y, start_z + i))

        # 2. [SỬA LỖI] Xác định vị trí các nhánh một cách tường minh
        branch_offsets = []
        middle_offset = (stem_len - 1) // 2
        top_offset = stem_len - 1
        
        if num_branches == 3: # Chữ E: nhánh ở đáy, giữa, và đỉnh
            branch_offsets = [0, middle_offset, top_offset]
        elif num_branches == 2: # Chữ F: nhánh ở giữa và đỉnh
            branch_offsets = [middle_offset, top_offset]

        # 3. Vẽ các nhánh từ các vị trí đã xác định
        for offset in branch_offsets:
            branch_start_pos: Coord = (start_x, y, start_z + offset)
            # Thêm các ô của nhánh vào placement_coords
            for i in range(1, branch_len + 1):
                branch_coord = (branch_start_pos[0] + i, y, branch_start_pos[2])
                placement_coords.add(branch_coord)


        # --- PHẦN 3: TẠO ĐƯỜNG ĐI (path_coords) HỢP LÝ ---
        
        path_coords = []
        current_pos = start_pos
        path_coords.append(current_pos)
        
        # Tạo một "tour" đi qua tất cả các nhánh
        last_z_on_stem = start_z

        for i, offset in enumerate(branch_offsets):
            branch_z = start_z + offset
            
            # Đi lên thân cây đến nhánh tiếp theo
            while current_pos[2] < branch_z:
                current_pos = add_vectors(current_pos, FORWARD_Z)
                path_coords.append(current_pos)
            
            # Lưu vị trí trên thân cây
            pos_on_stem = current_pos
            
            # Đi ra hết nhánh
            for _ in range(branch_len):
                current_pos = add_vectors(current_pos, FORWARD_X)
                path_coords.append(current_pos)

            # Nếu không phải nhánh cuối cùng, đi ngược vào lại
            if i < len(branch_offsets) - 1:
                for _ in range(branch_len):
                    current_pos = add_vectors(current_pos, BACKWARD_X)
                    path_coords.append(current_pos) # Thêm cả đường về
        
        target_pos = current_pos # Đích là ở cuối nhánh trên cùng
        
        return PathInfo(
            start_pos=start_pos,
            target_pos=target_pos,
            path_coords=list(dict.fromkeys(path_coords)),
            placement_coords=list(placement_coords)
        )