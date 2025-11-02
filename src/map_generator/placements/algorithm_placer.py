# src/map_generator/placements/algorithm_placer.py

from .base_placer import BasePlacer
from src.map_generator.models.path_info import PathInfo
from src.utils.randomizer import shuffle_list
import random

class AlgorithmPlacer(BasePlacer):
    """
    Đặt các đối tượng cho các bài toán thuật toán phức tạp.
    
    Placer này hoạt động với các Topology như ComplexMaze, nơi không có
    đường đi định trước. Nó chỉ đặt mục tiêu ở một vị trí khó,
    buộc người chơi phải tự thiết kế thuật toán để tìm ra nó.
    """

    def place_items(self, path_info: PathInfo, params: dict) -> dict:
        """
        Nhận một map mê cung và đặt các vật phẩm vào các vị trí chiến lược
        (ví dụ: ngõ cụt) để tạo ra thử thách tìm kiếm.

        Args:
            path_info (PathInfo): Thông tin từ ComplexMazeTopology, chủ yếu
                                  chứa chướng ngại vật (tường).
            params (dict): Có thể chứa 'items_to_place'.

        Returns:
            dict: Một dictionary chứa layout map hoàn chỉnh.
        """
        print("    LOG: Placing items with 'algorithm' logic...")
        
        items = [] # Danh sách vật phẩm sẽ được tạo
        obstacles = path_info.obstacles.copy() # Kế thừa các chướng ngại vật (tường) từ topology
        items_to_place = params.get('items_to_place', []) # Lấy danh sách item cần đặt từ curriculum
        if not isinstance(items_to_place, list): # Đảm bảo nó luôn là một list
            items_to_place = [items_to_place]

        # [SỬA LỖI] Logic tìm ngõ cụt (dead ends) được viết lại hoàn toàn.
        path_coords_set = set(path_info.path_coords)
        dead_ends = []

        # Duyệt qua tất cả các ô đường đi để tìm ngõ cụt
        for coord in path_info.path_coords:
            # Bỏ qua điểm bắt đầu và kết thúc
            if coord == path_info.start_pos or coord == path_info.target_pos:
                continue

            x, y, z = coord
            neighbor_count = 0
            # Kiểm tra 4 hàng xóm trên mặt phẳng XZ
            for dx, dz in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                neighbor = (x + dx, y, z + dz)
                if neighbor in path_coords_set:
                    neighbor_count += 1
            
            # Một ô là ngõ cụt nếu nó chỉ có 1 hàng xóm là đường đi
            if neighbor_count == 1:
                dead_ends.append(coord)

        print(f"    LOG: (AlgorithmPlacer) Tìm thấy {len(dead_ends)} vị trí ngõ cụt.")

        # [CẢI TIẾN] Logic đặt vật phẩm mới để đảm bảo đặt đủ số lượng
        if items_to_place:
            # 1. Tạo danh sách các vị trí có thể đặt, ưu tiên ngõ cụt
            random.shuffle(dead_ends)
            placement_coords = dead_ends

            # 2. Nếu số ngõ cụt không đủ, lấy thêm các vị trí ngẫu nhiên
            # trên đường đi (trừ start/target và các vị trí đã chọn).
            if len(placement_coords) < len(items_to_place):
                print(f"   - ⚠️ Cảnh báo: Số ngõ cụt ({len(dead_ends)}) ít hơn số vật phẩm yêu cầu ({len(items_to_place)}). Sẽ đặt ở các vị trí ngẫu nhiên khác.")
                
                # Lấy tất cả các ô đường đi có thể đặt
                other_possible_coords = list(path_coords_set - set(placement_coords) - {path_info.start_pos, path_info.target_pos})
                random.shuffle(other_possible_coords)
                
                # Bổ sung vào danh sách các vị trí có thể đặt
                needed_more = len(items_to_place) - len(placement_coords)
                placement_coords.extend(other_possible_coords[:needed_more])
            
            # 3. Đặt vật phẩm vào các vị trí đã chọn (tối đa bằng số vị trí tìm được)
            for i in range(min(len(items_to_place), len(placement_coords))):
                item_type = items_to_place[i]
                pos = placement_coords[i]
                items.append({"type": item_type, "pos": pos})
                print(f"      -> Đã đặt '{item_type}' tại vị trí {pos}")

        return {
            "start_pos": path_info.start_pos,
            "target_pos": path_info.target_pos,
            "items": items,
            "obstacles": obstacles
        }