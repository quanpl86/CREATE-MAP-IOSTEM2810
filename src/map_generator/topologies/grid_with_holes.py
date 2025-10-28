import random
from .base_topology import BaseTopology
from src.map_generator.models.path_info import PathInfo, Coord

class GridWithHolesTopology(BaseTopology):
    """
    Tạo ra một khu vực lưới hình chữ nhật với các ô ngẫu nhiên bị loại bỏ,
    tạo thành các "hố" hoặc "vực".
    """

    def generate_path_info(self, grid_size: tuple, params: dict) -> PathInfo:
        """
        Sinh ra một lưới với các hố ngẫu nhiên, đảm bảo có đường đi.

        Args:
            params (dict):
                - grid_width (int): Chiều rộng của khu vực lưới.
                - grid_depth (int): Chiều sâu của khu vực lưới.
                - hole_chance (float): Xác suất một ô là hố (0.0 đến 1.0).

        Returns:
            PathInfo: Một đối tượng chứa thông tin về lưới.
        """
        print("    LOG: Generating 'grid_with_holes' topology...")

        width = params.get('grid_width', 8)
        depth = params.get('grid_depth', 8)
        hole_chance = params.get('hole_chance', 0.25)
        y = 0

        if width > grid_size[0] - 2: width = grid_size[0] - 2
        if depth > grid_size[2] - 2: depth = grid_size[2] - 2

        start_x_offset = random.randint(1, grid_size[0] - width - 1)
        start_z_offset = random.randint(1, grid_size[2] - depth - 1)

        start_pos: Coord = (start_x_offset, y, start_z_offset)
        target_pos: Coord = (start_x_offset + width - 1, y, start_z_offset + depth - 1)

        main_path_coords = []
        for i in range(width):
            pos = (start_x_offset + i, y, start_z_offset)
            main_path_coords.append(pos)
        for i in range(1, depth):
            pos = (start_x_offset + width - 1, y, start_z_offset + i)
            main_path_coords.append(pos)
        
        main_path_set = set(main_path_coords)

        all_grid_coords = set()
        potential_holes = set()
        for x in range(width):
            for z in range(depth):
                current_pos = (start_x_offset + x, y, start_z_offset + z)
                all_grid_coords.add(current_pos)
                if current_pos not in main_path_set and random.random() < hole_chance:
                    potential_holes.add(current_pos)

        placement_coords = list(all_grid_coords - potential_holes)
        
        # ====================================================================
        # === ĐÂY LÀ DÒNG CODE QUAN TRỌNG NHẤT CẦN KIỂM TRA ===
        # === Hãy chắc chắn rằng "type" là "pit" (hố), KHÔNG PHẢI "wall" (tường) ===
        # ====================================================================
        obstacles = [{"type": "pit", "pos": pos} for pos in potential_holes]

        return PathInfo(
            start_pos=start_pos,
            target_pos=target_pos,
            path_coords=main_path_coords,
            placement_coords=placement_coords,
            obstacles=obstacles,
        )