# src/map_generator/topologies/staircase.py

import random
from .base_topology import BaseTopology
from src.map_generator.models.path_info import PathInfo, Coord
from src.utils.geometry import add_vectors, scale_vector, FORWARD_X, UP_Y

class StaircaseTopology(BaseTopology):
    """
    Tạo ra một cấu trúc cầu thang đi lên đều đặn.
    
    Đây là dạng map lý tưởng để dạy về vòng lặp 'for' kết hợp với
    lệnh 'jump' để di chuyển trong không gian 3D.
    """
    
    def generate_path_info(self, grid_size: tuple, params: dict) -> PathInfo:
        """
        Tạo ra một cầu thang với số bậc và hướng ngẫu nhiên.

        Args:
            params (dict):
                - num_steps (int): Số bậc thang.
                - step_size (int): Chiều dài của mỗi bậc (mặt phẳng). Mặc định là 1.

        Returns:
            PathInfo: Một đối tượng chứa thông tin về cầu thang.
                      'path_coords' sẽ chứa tọa độ của đỉnh mỗi bậc thang.
        """
        print("    LOG: Generating 'staircase' topology...")
        
        # Lấy số bậc thang từ params, mặc định là 5
        num_steps = params.get('num_steps', random.randint(4, 6))
        step_size = params.get('step_size', 1) # Tham số mới cho chiều dài bậc

        # Đảm bảo cầu thang không quá dài/cao so với map
        max_dim = min(grid_size[0], grid_size[1], grid_size[2]) - 2
        if num_steps * step_size >= max_dim:
            num_steps = max_dim -1
        
        # Chọn hướng đi tới trên mặt phẳng XZ (tiến hoặc lùi theo X hoặc Z)
        axis = random.choice(['x', 'z'])
        direction = random.choice([1, -1])

        # Tính toán vị trí bắt đầu an toàn để cầu thang không ra ngoài biên
        start_y = 0
        if axis == 'x':
            start_x = random.randint(0, grid_size[0] - (num_steps * step_size + 2)) if direction == 1 else random.randint(num_steps * step_size + 1, grid_size[0] - 1)
            start_z = random.randint(0, grid_size[2] - 1)
        else: # axis == 'z'
            start_z = random.randint(0, grid_size[2] - (num_steps * step_size + 2)) if direction == 1 else random.randint(num_steps * step_size + 1, grid_size[2] - 1)
            start_x = random.randint(0, grid_size[0] - 1)
        
        start_pos: Coord = (start_x, start_y, start_z)

        # Tạo đường đi (tọa độ của đỉnh các bậc thang)
        path_coords: list[Coord] = []
        obstacles = []
        current_pos = list(start_pos)
        
        # Vòng lặp để xây dựng từng bậc thang
        for i in range(num_steps):
            # Di chuyển tới theo hướng đã chọn với chiều dài step_size
            for _ in range(step_size):
                if axis == 'x':
                    current_pos[0] += direction
                else: # axis == 'z'
                    current_pos[2] += direction
                path_coords.append(tuple(current_pos))
            
            # Đi lên một bậc (tăng tọa độ Y)
            current_pos[1] += 1
            path_coords.append(tuple(current_pos))
            
        # Vị trí đích là đỉnh của bậc thang cuối cùng
        target_pos = path_coords[-1]

        # [CẢI TIẾN] Định nghĩa các bậc thang là các khối vật lý để solver có thể "jump" lên.
        # Chúng ta sẽ coi mỗi ô đi lên là một "obstacle" có thể đứng được.
        stair_blocks = [pos for pos in path_coords if pos[1] > start_pos[1]]
        obstacles.extend([{"type": "obstacle", "modelKey": "ground.checker", "pos": pos} for pos in stair_blocks])

        return PathInfo(
            start_pos=start_pos,
            target_pos=target_pos,
            path_coords=path_coords,
            obstacles=obstacles
        )