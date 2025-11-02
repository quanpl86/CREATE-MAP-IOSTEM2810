# src/map_generator/topologies/swift_playground_maze.py
import random
from typing import List, Set
from .base_topology import BaseTopology
from src.map_generator.models.path_info import PathInfo, Coord
from src.utils.geometry import add_vectors, UP_Y


class SwiftPlaygroundMazeTopology(BaseTopology):
    """
    Tạo ra một mê cung nhiều tầng với các sàn nhỏ được nối với nhau bằng các bậc thang.
    Đảm bảo có một đường đi liên tục từ điểm bắt đầu đến điểm kết thúc.
    """

    def _is_valid(self, x, y, z):
        return 0 <= x < 14 and 0 <= y < 12 and 0 <= z < 14

    def _add_platform(self, placement: Set[Coord], cx, cz, y, size=3):
        """Sàn vuông tại Y cố định"""
        for dx in range(-1, 2):
            for dz in range(-1, 2):
                px, pz = cx + dx, cz + dz
                if self._is_valid(px, y, pz):
                    coord = (px, y, pz)
                    placement.add(coord)

    def _create_path_segment(self, start_coord: Coord, end_coord: Coord) -> List[Coord]:
        """Tạo một đoạn đường đi thẳng (ngang hoặc dọc) giữa hai điểm."""
        path = []
        current = list(start_coord)
        dx = 1 if end_coord[0] > start_coord[0] else -1 if end_coord[0] < start_coord[0] else 0
        dz = 1 if end_coord[2] > start_coord[2] else -1 if end_coord[2] < start_coord[2] else 0
        
        while tuple(current) != end_coord:
            if current[0] != end_coord[0]:
                current[0] += dx
            elif current[2] != end_coord[2]:
                current[2] += dz
            path.append(tuple(current))
        return path

    def generate_path_info(self, grid_size: tuple, params: dict) -> PathInfo:
        print("    LOG: Generating 'swift_playground_maze' topology...")

        placement_coords: Set[Coord] = set()
        path_coords: List[Coord] = []
        obstacles: List[dict] = []

        # Các điểm trung tâm của mỗi sàn (platform)
        # [SỬA LỖI] Tính toán lại waypoints để đảm bảo khoảng cách 2 ô giữa các cạnh sàn.
        # Khoảng cách giữa các tâm là 5 ô (1 (bán kính) + 2 (gap) + 1 (bán kính) + 1 (tâm)).
        waypoints = [
            (3, 0, 3),    # Sàn 1 (Start)
            (8, 2, 3),    # Sàn 2 (cách 5 ô theo trục X)
            (8, 4, 8),    # Sàn 3 (cách 5 ô theo trục Z)
            (13, 6, 8),   # Sàn 4 (cách 5 ô theo trục X)
            (13, 8, 13),  # Sàn 5 (cách 5 ô theo trục Z)
            (8, 10, 13),  # Sàn 6 (Target, cách 5 ô theo trục X)
        ]

        # Tạo sàn đầu tiên và đặt điểm bắt đầu
        start_pos = waypoints[0]
        path_coords.append(start_pos)
        self._add_platform(placement_coords, start_pos[0], start_pos[2], start_pos[1])

        # Nối các waypoint lại với nhau
        for i in range(len(waypoints) - 1):
            p1 = waypoints[i]
            p2 = waypoints[i+1]

            # 1. Đi ngang trên cùng một sàn
            # Đi từ tâm p1 ra rìa sàn (cách tâm 1 ô) theo hướng của p2.
            horizontal_dir = (1 if p2[0] > p1[0] else -1 if p2[0] < p1[0] else 0, 0, 1 if p2[2] > p1[2] else -1 if p2[2] < p1[2] else 0)
            edge_p1 = add_vectors(p1, horizontal_dir)
            path_coords.extend(self._create_path_segment(p1, edge_p1))

            # 2. [REWRITTEN] Tạo cầu thang 2 bậc để nối khoảng trống 2 ô và chênh lệch 2 độ cao.
            current_pos = edge_p1
            
            # Bậc 1: Đi tới 1 ô, đặt bậc thang đầu tiên.
            step1_pos = add_vectors(current_pos, horizontal_dir)
            placement_coords.add(step1_pos)
            path_coords.append(step1_pos)
            current_pos = step1_pos

            # Bậc 2 (bước nhảy):
            # - Bệ đỡ (trigger) cho bước nhảy nằm ngay trước mặt.
            # - Điểm đáp (landing) nằm chéo lên trên.
            stair_base_pos = add_vectors(current_pos, horizontal_dir)
            landing_pos = add_vectors(stair_base_pos, UP_Y)

            # Thêm các khối cần thiết để vẽ và để solver xử lý.
            # [CẢI TIẾN] Xóa modelKey cứng. Việc gán modelKey sẽ do generate_all_maps.py
            # xử lý dựa trên asset_theme.
            obstacles.append({"type": "obstacle", "pos": stair_base_pos})
            placement_coords.add(stair_base_pos)
            placement_coords.add(landing_pos)

            # Cập nhật đường đi và vị trí của người chơi.
            path_coords.append(landing_pos)
            current_pos = landing_pos

            # Bậc 3 (tương tự bậc 1, để hoàn thành chênh lệch 2 độ cao):
            stair_base_pos_2 = add_vectors(current_pos, horizontal_dir)
            landing_pos_2 = add_vectors(stair_base_pos_2, UP_Y)

            obstacles.append({"type": "obstacle", "pos": stair_base_pos_2})
            placement_coords.add(stair_base_pos_2)
            placement_coords.add(landing_pos_2)
            path_coords.append(landing_pos_2)
            current_pos = landing_pos_2

            # 3. Tạo sàn tại waypoint tiếp theo
            self._add_platform(placement_coords, p2[0], p2[2], p2[1])
            # Đi từ cuối bậc thang vào trung tâm sàn mới
            path_coords.extend(self._create_path_segment(current_pos, p2))

        target_pos = path_coords[-1]

        return PathInfo(
            start_pos=start_pos,
            target_pos=target_pos,
            path_coords=list(dict.fromkeys(path_coords)), # Xóa trùng lặp, giữ thứ tự
            placement_coords=list(placement_coords),
            obstacles=obstacles
        )