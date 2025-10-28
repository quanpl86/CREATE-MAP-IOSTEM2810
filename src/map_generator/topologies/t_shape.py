import random
from .base_topology import BaseTopology
from src.map_generator.models.path_info import PathInfo, Coord
from src.utils.geometry import add_vectors, FORWARD_X, FORWARD_Z, BACKWARD_X

class TShapeTopology(BaseTopology):
    """
    Tạo ra một con đường hình chữ T trên mặt phẳng 2D.
    Lý tưởng cho các bài học về tuần tự lệnh, hàm, hoặc các cấu trúc điều kiện
    khi người chơi phải quyết định rẽ trái hay phải ở ngã ba.
    """

    def generate_path_info(self, grid_size: tuple, params: dict) -> PathInfo:
        """
        Tạo ra một đường đi hình chữ T.

        Args:
            params (dict):
                - stem_length (int): Độ dài của "thân" chữ T.
                - bar_length (int): Độ dài của "thanh ngang" chữ T.

        Returns:
            PathInfo: Một đối tượng chứa thông tin về đường đi.
        """
        print("    LOG: Generating 't_shape' topology...")

        # Lấy độ dài các cạnh từ params, hoặc dùng giá trị ngẫu nhiên
        stem_len = params.get('stem_length', random.randint(3, 5))
        bar_len = params.get('bar_length', random.randint(4, 6))
        if bar_len % 2 == 0: bar_len += 1 # Đảm bảo thanh ngang có điểm chính giữa

        bar_side_len = bar_len // 2

        # Đảm bảo hình dạng nằm gọn trong map
        start_x = random.randint(bar_side_len + 1, grid_size[0] - bar_side_len - 2)
        start_z = random.randint(1, grid_size[2] - stem_len - 2)
        y = 0
        start_pos: Coord = (start_x, y, start_z)
 
        path_coords: list[Coord] = [] # Đường đi cho solver
        placement_coords: list[Coord] = [start_pos] # Toàn bộ hình dạng chữ T
        current_pos = start_pos
 
        # 1. Vẽ thân chữ T (đi theo trục Z)
        for _ in range(stem_len):
            current_pos = add_vectors(current_pos, FORWARD_Z)
            path_coords.append(current_pos)
            placement_coords.append(current_pos)
 
        junction_pos = current_pos
 
        # 2. Vẽ thanh ngang (đi theo trục X)
        # Vẽ nhánh phải
        temp_pos = junction_pos
        for _ in range(bar_side_len):
            temp_pos = add_vectors(temp_pos, FORWARD_X)
            placement_coords.append(temp_pos)
 
        # Vẽ nhánh trái
        temp_pos = junction_pos
        for _ in range(bar_side_len):
            temp_pos = add_vectors(temp_pos, BACKWARD_X)
            placement_coords.append(temp_pos)
 
        # 3. Chọn điểm đích và hoàn thiện đường đi chính
        # Ví dụ: đích ở cuối nhánh trái
        target_pos = (start_x - bar_side_len, y, start_z + stem_len)
        
        # Hoàn thiện path_coords từ ngã ba đến đích
        temp_pos = junction_pos
        for _ in range(bar_side_len):
            temp_pos = add_vectors(temp_pos, BACKWARD_X)
            path_coords.append(temp_pos)
 
        return PathInfo(
            start_pos=start_pos,
            target_pos=target_pos,
            path_coords=list(dict.fromkeys(path_coords)),
            placement_coords=list(dict.fromkeys(placement_coords))
        )