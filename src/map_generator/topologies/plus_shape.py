import random
from .base_topology import BaseTopology
from src.map_generator.models.path_info import PathInfo, Coord
from src.utils.geometry import add_vectors, FORWARD_X, BACKWARD_X, FORWARD_Z, BACKWARD_Z

class PlusShapeTopology(BaseTopology):
    """
    Tạo ra một con đường hình dấu cộng (+) trên mặt phẳng 2D.
    Lý tưởng cho các bài học về cấu trúc điều kiện (if/else) hoặc hàm,
    khi người chơi phải khám phá các nhánh khác nhau.
    """

    def generate_path_info(self, grid_size: tuple, params: dict) -> PathInfo:
        """
        Tạo ra một đường đi hình dấu cộng.

        Args:
            params (dict):
                - arm_length (int): Độ dài của mỗi nhánh tính từ tâm.

        Returns:
            PathInfo: Một đối tượng chứa thông tin về đường đi.
        """
        print("    LOG: Generating 'plus_shape' topology...")

        # Lấy độ dài nhánh từ params, hoặc dùng giá trị ngẫu nhiên
        arm_len = params.get('arm_length', random.randint(2, 4))

        # Đảm bảo hình dạng nằm gọn trong map
        required_size = arm_len * 2 + 1 # Kích thước tổng thể của dấu cộng
        
        # Chọn vị trí tâm an toàn
        center_x = random.randint(arm_len + 1, grid_size[0] - arm_len - 2)
        center_z = random.randint(arm_len + 1, grid_size[2] - arm_len - 2)
        y = 0
        center_pos: Coord = (center_x, y, center_z)

        placement_coords: list[Coord] = [center_pos]
        
        # 1. Vẽ 4 nhánh và thêm vào placement_coords
        directions = [FORWARD_X, BACKWARD_X, FORWARD_Z, BACKWARD_Z]
        arm_ends = []

        for direction in directions:
            current_pos = center_pos
            for _ in range(arm_len):
                current_pos = add_vectors(current_pos, direction)
                placement_coords.append(current_pos)
            arm_ends.append(current_pos)

        # 2. Chọn điểm bắt đầu và kết thúc ngẫu nhiên từ các đầu nhánh
        random.shuffle(arm_ends)
        start_pos = arm_ends.pop()
        target_pos = arm_ends.pop()

        # 3. Tạo đường đi liên tục cho solver (đi từ start -> center -> target)
        path_coords: list[Coord] = []
        
        # Đi từ start về center
        # (Tạo một đường đi ngược lại từ center về start, rồi đảo ngược nó)
        temp_path_to_start = []
        temp_pos = center_pos
        while temp_pos != start_pos:
            # Tìm hướng đi từ center đến start
            move = (start_pos[0] - temp_pos[0], 0, start_pos[2] - temp_pos[2])
            move_normalized = (int(move[0]/abs(move[0])) if move[0] != 0 else 0, 0, int(move[2]/abs(move[2])) if move[2] != 0 else 0)
            temp_pos = add_vectors(temp_pos, move_normalized)
            temp_path_to_start.append(temp_pos)
        path_coords.extend(reversed(temp_path_to_start))

        # Đi từ center đến target
        path_coords.extend([p for p in placement_coords if p[1] == y and (p[0] >= center_x and p[2] == center_z and p[0] <= target_pos[0]) or (p[2] >= center_z and p[0] == center_x and p[2] <= target_pos[2]) or (p[0] <= center_x and p[2] == center_z and p[0] >= target_pos[0]) or (p[2] <= center_z and p[0] == center_x and p[2] >= target_pos[2])])

        return PathInfo(
            start_pos=start_pos,
            target_pos=target_pos,
            path_coords=list(dict.fromkeys(path_coords)),
            placement_coords=list(dict.fromkeys(placement_coords))
        )