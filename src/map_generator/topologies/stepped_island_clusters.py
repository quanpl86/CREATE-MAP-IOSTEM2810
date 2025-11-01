# src/map_generator/topologies/stepped_island_clusters.py

import random
from .base_topology import BaseTopology
from src.map_generator.models.path_info import PathInfo, Coord
from src.utils.geometry import add_vectors, FORWARD_X, UP_Y

class SteppedIslandClustersTopology(BaseTopology):
    """
    Tạo ra nhiều cụm đảo, với mỗi cụm ở một độ cao khác nhau,
    được nối với nhau bằng các bậc thang.
    """

    def _create_island(self, top_left_corner: Coord, size: int = 2) -> list[Coord]:
        """Tạo một hòn đảo hình vuông."""
        x, y, z = top_left_corner
        coords = []
        for i in range(size):
            for j in range(size):
                coords.append((x + i, y, z + j))
        return coords

    def _create_staircase(self, start_point: Coord, steps: int) -> list[Coord]:
        """
        Tạo cầu thang đi được (zigzag) theo hướng +X.
        Mỗi bậc gồm 1 bước ngang và 1 bước lên.
        """
        path = []
        current_pos = start_point
        for _ in range(steps):
            # Bước 1: Đi ngang
            current_pos = add_vectors(current_pos, FORWARD_X)
            path.append(current_pos)
            # Bước 2: Đi lên
            current_pos = add_vectors(current_pos, UP_Y)
            path.append(current_pos)
        return path

    def _create_bridge(self, start_point: Coord, end_point: Coord) -> list[Coord]:
        """Tạo một cây cầu phẳng từ start đến end theo trục X."""
        path = []
        curr_x, y, z = start_point
        end_x = end_point[0]
        step = 1 if end_x > curr_x else -1
        # Bỏ qua điểm đầu tiên vì nó đã tồn tại
        while curr_x != end_x:
            curr_x += step
            path.append((curr_x, y, z))
        return path

    def generate_path_info(self, grid_size: tuple, params: dict) -> PathInfo:
        """Sinh ra các cụm đảo ở các độ cao khác nhau."""
        print("    LOG: Generating 'stepped_island_clusters' topology...")

        num_clusters = params.get('num_clusters', 2)
        islands_per_cluster = params.get('islands_per_cluster', 2)
        cluster_spacing = params.get('cluster_spacing', 8)
        height_step = params.get('height_step', 2)

        start_x = 2
        start_z = grid_size[2] // 2
        y = 0

        path_coords: list[Coord] = []
        placement_coords: list[Coord] = []
        obstacles = []

        # Điểm bắt đầu của cụm đầu tiên
        last_exit_point = (start_x -1, y, start_z)

        for i in range(num_clusters):
            # Tạo cụm đảo đầu tiên
            island_base_y = y + i * height_step
            # Điểm vào của cụm là điểm ra của cầu thang trước đó
            cluster_entry_point = last_exit_point
            
            # Nối các đảo trong cụm
            for j in range(islands_per_cluster):
                island_x = cluster_entry_point[0] + 1
                island_z = start_z if j == 0 else start_z + (j * 4) # Đặt các đảo cách nhau
                
                # Điểm vào của đảo này
                current_island_entry = (island_x, island_base_y, cluster_entry_point[2])
                
                # Tạo cầu nối từ điểm trước đó đến đảo này
                bridge = self._create_bridge(last_exit_point, current_island_entry)
                path_coords.extend(bridge)
                placement_coords.extend(bridge)
                
                # Tạo đảo
                island = self._create_island((current_island_entry[0], island_base_y, start_z), size=2)
                path_coords.extend(island) # Đường đi trên đảo có thể đơn giản là đi hết các khối
                placement_coords.extend(island)
                
                # Cập nhật điểm ra cho đảo/cầu tiếp theo
                last_exit_point = (island[-1][0], island_base_y, island[-1][2])

            # Nếu chưa phải cụm cuối, tạo cầu thang đi lên
            if i < num_clusters - 1:
                stair_coords = self._create_staircase(last_exit_point, height_step)
                path_coords.extend(stair_coords) # Thêm vào đường đi của solver
                # [CHUẨN HÓA] Định nghĩa bậc thang là một loại chướng ngại vật (obstacle) có thể đứng lên được.
                # Sử dụng modelKey 'ground.checker' để nó trông giống một khối có thể đi được.
                obstacles.extend([{"type": "obstacle", "modelKey": "ground.checker", "pos": pos} for pos in stair_coords])
                last_exit_point = stair_coords[-1]

        # Tạo nền móng cho tất cả các khối đã đặt
        coords_with_foundation = set()
        for x, y_coord, z in placement_coords:
            for y_level in range(y_coord + 1):
                coords_with_foundation.add((x, y_level, z))
        
        # Dọn dẹp
        final_path = list(dict.fromkeys(path_coords)) # Xóa trùng lặp, giữ thứ tự
        final_placement = list(coords_with_foundation)

        start_pos = final_path[0]
        target_pos = final_path[-1]
        
        # Đảm bảo người chơi có chỗ đứng ban đầu
        if start_pos not in final_placement:
            final_placement.append(start_pos)
            final_placement.append((start_pos[0], start_pos[1]-1, start_pos[2]))


        return PathInfo(
            start_pos=start_pos,
            target_pos=target_pos,
            path_coords=final_path,
            placement_coords=final_placement,
            obstacles=obstacles
        )