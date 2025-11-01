# src/map_generator/placements/function_placer.py

import random
from .base_placer import BasePlacer
from src.map_generator.models.path_info import PathInfo

class FunctionPlacer(BasePlacer):
    """
    Đặt các vật phẩm để khuyến khích người chơi sử dụng Hàm và Tham số.
    
    Placer này hoạt động bằng cách đặt vật phẩm lên các mẫu hình (patterns)
    mà Topology đã tạo ra, làm cho sự lặp lại của các mẫu hình đó trở nên
    rõ ràng và trực quan.
    """

    def place_items(self, path_info: PathInfo, params: dict) -> dict: # noqa
        """
        [REWRITTEN] Đặt vật phẩm và chướng ngại vật dựa trên params.
        - Nếu có 'obstacles' hoặc 'items_to_place' trong params, sẽ đặt chúng một cách chọn lọc.
        - Nếu không, sẽ quay về hành vi mặc định: đặt 'crystal' ở mọi nơi.

        Args:
            path_info (PathInfo): Thông tin đường đi từ một lớp Topology
                                  (ví dụ: SymmetricalIslandsTopology).
            params (dict): Các tham số bổ sung.
        """
        print("    LOG: Placing items with 'function' or 'parameter' logic...")

        coords_to_place_on = path_info.placement_coords if path_info.placement_coords else path_info.path_coords
        possible_coords = [p for p in coords_to_place_on if p != path_info.start_pos and p != path_info.target_pos]
        random.shuffle(possible_coords)

        items = []
        # Kế thừa các chướng ngại vật đã có từ topology (ví dụ: bậc thang)
        obstacles = path_info.obstacles.copy()

        # --- [NEW LOGIC] Xử lý đặt đối tượng có chọn lọc ---
        num_obstacles = params.get('obstacles', 0)
        items_to_place_param = params.get('items_to_place', [])
        items_to_place = items_to_place_param if isinstance(items_to_place_param, list) else [items_to_place_param]

        # Nếu có yêu cầu đặt chướng ngại vật hoặc các item cụ thể
        if num_obstacles > 0 or items_to_place:
            # 1. Đặt chướng ngại vật trước
            # [THOROUGH UPGRADE] Logic an toàn cho map 3D
            # Không đặt thêm chướng ngại vật nếu map là loại có bậc thang,
            # để tránh xung đột với các khối đã có sẵn.
            map_type = params.get('map_type', '')
            is_3d_map = map_type in ['staircase', 'staircase_3d', 'hub_with_stepped_islands', 'stepped_island_clusters']

            for _ in range(num_obstacles):
                if not possible_coords:
                    print("   - ⚠️ Cảnh báo: Không đủ vị trí để đặt chướng ngại vật.")
                    break
                if is_3d_map:
                    print(f"   - ℹ️ INFO: Bỏ qua việc đặt thêm chướng ngại vật cho map 3D '{map_type}'.")
                    break
                else:
                    pos = possible_coords.pop(0)
                    obstacles.append({"type": "obstacle", "modelKey": "wall.brick01", "pos": pos})

            # 2. Đặt các vật phẩm vào các vị trí còn lại
            for item_type in items_to_place:
                if not possible_coords:
                    print(f"   - ⚠️ Cảnh báo: Không đủ vị trí để đặt vật phẩm '{item_type}'.")
                    break
                pos = possible_coords.pop(0)
                if item_type == "switch":
                    items.append({"type": "switch", "pos": pos, "initial_state": random.choice(["on", "off"])})
                else:
                    items.append({"type": item_type, "pos": pos})
        else:
            # --- HÀNH VI MẶC ĐỊNH (Legacy) ---
            # Nếu không có yêu cầu cụ thể, đặt 'crystal' ở mọi nơi.
            # Điều này giữ cho các map cũ (như symmetrical_islands) hoạt động đúng.
            # [THOROUGH UPGRADE] Logic đặt vật phẩm chiến lược
            map_type = params.get('map_type', '')
            if map_type in ['symmetrical_islands', 'plus_shape_islands', 'stepped_island_clusters', 'hub_with_stepped_islands']:
                 # Với map dạng đảo, ưu tiên đặt 1 item trên mỗi "đảo" hoặc khu vực.
                 # Giả định placement_coords chứa các tọa độ của đảo.
                 print("    LOG: (FunctionPlacer) Áp dụng chiến lược đặt item trên mỗi đảo.")
                 # Đây là một cách ước tính, cần logic phức tạp hơn để xác định chính xác "đảo"
                 num_islands = params.get('num_islands', params.get('num_clusters', 4))
                 selected_coords = random.sample(possible_coords, min(num_islands, len(possible_coords)))
                 items = [{"type": "crystal", "pos": pos} for pos in selected_coords]
            elif map_type == 'interspersed_path':
                 print("    LOG: (FunctionPlacer) Áp dụng chiến lược đặt item ở cuối nhánh.")
                 # Logic này cần được cải tiến trong Topology để trả về "end_of_branch_coords"
                 items = [{"type": "crystal", "pos": pos} for pos in possible_coords] # Tạm thời giữ nguyên
            else:
                 items = [{"type": "crystal", "pos": pos} for pos in possible_coords]

        return {
            "start_pos": path_info.start_pos,
            "target_pos": path_info.target_pos,
            "items": items,
            "obstacles": obstacles
        }