# src/map_generator/topologies/plowing_field.py

import random
from .base_topology import BaseTopology
from src.map_generator.models.path_info import PathInfo, Coord
from src.utils.geometry import add_vectors, FORWARD_X, FORWARD_Z, BACKWARD_X

class PlowingFieldTopology(BaseTopology):
    """
    Tạo ra một con đường đi theo kiểu "luống cày" (zig-zag qua lại)
    để lấp đầy một khu vực hình chữ nhật.
    
    Đây là dạng map kinh điển để dạy về vòng lặp lồng nhau.
    """
    
    def generate_path_info(self, grid_size: tuple, params: dict) -> PathInfo:
        """
        Tạo ra một đường đi zig-zag qua các hàng và cột.

        Args:
            params (dict): Cần chứa 'rows' và 'cols'.

        Returns:
            PathInfo: Một đối tượng chứa thông tin về đường đi luống cày.
        """
        print("    LOG: Generating 'plowing_field' topology...")
        
        rows = params.get('rows', random.randint(4, 6))
        cols = params.get('cols', random.randint(5, 7))

        # Đảm bảo khu vực này nằm gọn trong map
        if cols > grid_size[0] - 2: cols = grid_size[0] - 2
        if rows > grid_size[2] - 2: rows = grid_size[2] - 2

        start_x = random.randint(1, grid_size[0] - cols - 1)
        start_z = random.randint(1, grid_size[2] - rows - 1)
        y = 0

        # [SỬA LỖI 2] Điểm bắt đầu của người chơi là điểm bắt đầu của đường đi
        start_pos: Coord = (start_x, y, start_z)
        
        path_coords: list[Coord] = [start_pos]
        current_pos = start_pos
        
        # [SỬA LỖI 3] Logic zig-zag được viết lại cho rõ ràng hơn
        for r in range(rows):
            # Xác định hướng đi cho hàng hiện tại
            # Hàng chẵn (0, 2, 4...) đi sang phải (FORWARD_X)
            # Hàng lẻ (1, 3, 5...) đi sang trái (BACKWARD_X)
            if r % 2 == 0:
                direction = FORWARD_X
            else:
                direction = BACKWARD_X
            
            # Đi hết một hàng (cols - 1 bước)
            for _ in range(cols - 1):
                current_pos = add_vectors(current_pos, direction)
                path_coords.append(current_pos)
            
            # Nếu chưa phải hàng cuối, đi xuống 1 bước để sang hàng mới
            if r < rows - 1:
                current_pos = add_vectors(current_pos, FORWARD_Z)
                path_coords.append(current_pos)

        target_pos = path_coords[-1]

        # [SỬA LỖI 1] Luôn cung cấp placement_coords
        # Trong trường hợp này, các khối đất chính là đường đi.
        return PathInfo(
            start_pos=start_pos,
            target_pos=target_pos,
            path_coords=path_coords,
            placement_coords=path_coords
        )