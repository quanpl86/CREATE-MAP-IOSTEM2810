# src/map_generator/topologies/symmetrical_islands.py

import random
from .base_topology import BaseTopology
from src.map_generator.models.path_info import PathInfo, Coord

class SymmetricalIslandsTopology(BaseTopology):
    """
    Tạo ra các khu vực (đảo) có cấu trúc giống hệt nhau, được ngăn cách
    bởi các khoảng trống hoặc hành lang.
    
    Đây là dạng map lý tưởng để dạy về việc nhận biết mẫu lặp lại
    và phân rã vấn đề thành các hàm có thể tái sử dụng.
    """

    def _create_island_pattern(self, top_left_corner: Coord, pattern_name: str) -> tuple[list[Coord], tuple[int, int]]:
        """
        Tạo ra một mẫu hình hòn đảo cụ thể.
        Hàm này có thể được thay đổi để tạo ra các mẫu phức tạp hơn.
        
        Args:
            top_left_corner (Coord): Tọa độ góc trên bên trái của hòn đảo.
            pattern_name (str): Tên của mẫu hình ('u_shape', 'l_shape', 'plus_shape', 'square_shape').
            
        Returns:
            tuple[list[Coord], tuple[int, int]]: Một tuple chứa:
                - Danh sách các tọa độ tạo nên con đường trên đảo.
                - Kích thước (width, depth) của mẫu hình đó.
        """
        x, y, z = top_left_corner
        path = []
        size = (0, 0)
        
        if pattern_name == 'l_shape':
            # Hình chữ L, kích thước 3x3
            path = [(x, y, z), (x, y, z + 1), (x, y, z + 2), (x + 1, y, z + 2), (x + 2, y, z + 2)]
            size = (3, 3)
        elif pattern_name == 'plus_shape':
            # Hình dấu cộng, kích thước 3x3
            path = [(x + 1, y, z), (x, y, z + 1), (x + 1, y, z + 1), (x + 2, y, z + 1), (x + 1, y, z + 2)]
            size = (3, 3)
        elif pattern_name == 'square_shape':
            # Hình vuông 3x3 rỗng ruột
            path = [
                (x, y, z), (x + 1, y, z), (x + 2, y, z),
                (x + 2, y, z + 1), (x + 2, y, z + 2),
                (x + 1, y, z + 2), (x, y, z + 2), (x, y, z + 1)
            ]
            size = (3, 3)
        else: # Mặc định là 'u_shape'
            # Tạo một mẫu hình chữ U đơn giản, kích thước 2x2
            # Path: (x,z) -> (x+1,z) -> (x+1,z+1) -> (x,z+1)
            path = [(x, y, z), (x + 1, y, z), (x + 1, y, z + 1), (x, y, z + 1)]
            size = (2, 2)
        
        return path, size

    def generate_path_info(self, grid_size: tuple, params: dict) -> PathInfo:
        """
        Tạo ra một chuỗi các hòn đảo giống hệt nhau.

        Args:
            params (dict): Có thể chứa 'num_islands' để tùy chỉnh số lượng đảo.

        Returns:
            PathInfo: Một đối tượng chứa thông tin về tất cả các hòn đảo.
        """
        print("    LOG: Generating 'symmetrical_islands' topology...")
        
        # --- (CẢI TIẾN) Đọc và ngẫu nhiên hóa số lượng đảo ---
        num_islands_param = params.get('num_islands', 2)
        if isinstance(num_islands_param, list) and len(num_islands_param) == 2:
            # Nếu num_islands là một khoảng [min, max], chọn ngẫu nhiên một giá trị
            num_islands = random.randint(num_islands_param[0], num_islands_param[1])
        else:
            # Nếu không, sử dụng giá trị được cung cấp hoặc mặc định
            num_islands = num_islands_param
            
        # [MỚI] Đọc loại mẫu hình đảo từ params
        island_pattern_name = params.get('island_pattern', 'u_shape')

        # --- (CẢI TIẾN) Tự động tính toán khoảng cách tối ưu giữa các đảo ---
        # Lấy kích thước của mẫu đảo để tính toán
        _, island_size = self._create_island_pattern((0,0,0), island_pattern_name)
        island_width = island_size[0]
        # Tổng chiều rộng mà tất cả các đảo chiếm dụng
        total_islands_width = num_islands * island_width
        # Không gian còn lại trên lưới để phân bổ cho các cây cầu
        available_spacing = grid_size[0] - total_islands_width - 2 # Trừ 2 cho lề an toàn
        
        # Khoảng cách giữa các góc bắt đầu của hai đảo liên tiếp
        # Nếu chỉ có 1 đảo, spacing không có ý nghĩa.
        island_spacing = island_width + (available_spacing // (num_islands - 1)) if num_islands > 1 else 0

        # Tính toán vị trí bắt đầu an toàn
        start_x = 1 
        start_z = random.randint(1, grid_size[2] - island_size[1] - 2) # Trừ kích thước đảo và lề
        y = 0
        
        start_pos: Coord = (start_x, y, start_z)
        
        # [CẢI TIẾN] Bắt đầu đường đi từ vị trí xuất phát
        all_path_coords: list[Coord] = [start_pos]
        island_placement_coords: list[Coord] = [] # [SỬA] Danh sách riêng cho tọa độ của các đảo
        
        # Vòng lặp để tạo ra các hòn đảo
        for i in range(num_islands):
            # Tọa độ góc của mỗi hòn đảo được tính toán dựa trên khoảng cách
            # [CẢI TIẾN] Nếu là đảo đầu tiên, góc chính là start_pos. Nếu không, tính toán.
            island_corner = (start_x + i * island_spacing, y, start_z) if i > 0 else start_pos
            
            # Tạo đường đi cho hòn đảo hiện tại
            island_path, _ = self._create_island_pattern(island_corner, island_pattern_name)
            island_placement_coords.extend(island_path) # Thêm vào danh sách placement
            
            # [CẢI TIẾN] Nối đường đi một cách liền mạch
            # Bỏ qua điểm đầu của island_path nếu nó đã có trong all_path_coords
            for p in island_path:
                if p not in all_path_coords:
                    all_path_coords.append(p)
            
            # Tạo "cây cầu" nối giữa các đảo (nếu không phải đảo cuối cùng)
            if i < num_islands - 1:
                # [CẢI TIẾN] Cầu nối liền mạch từ điểm cuối của đảo hiện tại
                bridge_start = all_path_coords[-1]
                bridge_end = (start_x + (i + 1) * island_spacing, y, start_z) # Điểm đầu của đảo tiếp theo
                
                # [SỬA LỖI] Logic tạo cầu mới để đảm bảo tính liên tục.
                # Bước 1: Đi từ điểm cuối của đảo (bridge_start) về lại trục Z chính (start_z).
                # Đi ngược theo trục Z.
                current_z = bridge_start[2]
                while current_z > start_z:
                    current_z -= 1
                    all_path_coords.append((bridge_start[0], y, current_z))
                
                # Bước 2: Đi từ vị trí hiện tại trên trục Z chính đến điểm bắt đầu của đảo tiếp theo.
                # Đi thẳng theo trục X.
                current_x = bridge_start[0]
                while current_x < bridge_end[0]:
                    current_x += 1
                    all_path_coords.append((current_x, y, start_z))


        target_pos = all_path_coords[-1]
        
        return PathInfo(
            start_pos=start_pos,
            target_pos=target_pos,
            path_coords=all_path_coords, # Chứa tất cả các điểm của các đảo và cầu
            placement_coords=island_placement_coords # [SỬA] Cung cấp tọa độ chỉ của các đảo
        )