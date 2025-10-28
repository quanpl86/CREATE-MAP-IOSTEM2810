import random
from .base_topology import BaseTopology
from src.map_generator.models.path_info import PathInfo, Coord

class StarShapeTopology(BaseTopology):
    def _draw_straight_line(self, start: Coord, direction: str, length: int) -> list[Coord]:
        """Vẽ đường thẳng theo hướng: 'up', 'down', 'left', 'right'"""
        path = [start]
        x, y, z = start
        for _ in range(length):
            if direction == 'up':    z -= 1
            elif direction == 'down':z += 1
            elif direction == 'left':x -= 1
            elif direction == 'right':x += 1
            path.append((x, y, z))
        return path

    def generate_path_info(self, grid_size: tuple, params: dict) -> PathInfo:
        print(" LOG: Generating 'star_shape' topology (walkable)...")
        arm_len = params.get('arm_length', 3)
        if arm_len < 2: arm_len = 2

        # Tâm ngôi sao
        center_x = grid_size[0] // 2
        center_z = grid_size[2] // 2
        center = (center_x, 0, center_z)

        # Tạo 5 cánh: mỗi cánh dài `arm_len`
        arms = [
            ('up',    arm_len),   # cánh 1
            ('right', arm_len),   # cánh 2
            ('down',  arm_len),   # cánh 4
            ('left',  arm_len),   # cánh 5
            ('up',    arm_len),   # cánh 1 (để quay lại)
        ]

        path_coords = [center]
        current_pos = center

        for direction, length in arms:
            segment = self._draw_straight_line(current_pos, direction, length)
            path_coords.extend(segment[1:])  # bỏ điểm đầu
            current_pos = segment[-1]

        # Loại bỏ trùng lặp (chỉ ở tâm)
        seen = set()
        unique_path = []
        for p in path_coords:
            if p not in seen:
                seen.add(p)
                unique_path.append(p)

        start_pos = unique_path[0]
        target_pos = unique_path[-1]  # quay lại tâm

        return PathInfo(
            start_pos=start_pos,
            target_pos=target_pos,
            path_coords=unique_path,
            placement_coords=unique_path
        )