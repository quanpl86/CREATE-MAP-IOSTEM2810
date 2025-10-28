# src/map_generator/generator.py
from .topologies.straight_line import StraightLineTopology
from .topologies.l_shape import LShapeTopology
from .topologies.u_shape import UShapeTopology
from .topologies.s_shape import SShapeTopology
from .topologies.zigzag import ZigzagTopology
from .topologies.triangle import TriangleTopology
from .topologies.h_shape import HShapeTopology
from .topologies.ef_shape import EFShapeTopology
from .topologies.plus_shape import PlusShapeTopology
from .topologies.arrow_shape import ArrowShapeTopology
from .topologies.t_shape import TShapeTopology
from .placements.sequencing_placer import SequencingPlacer
from .placements.for_loop_placer import ForLoopPlacer
from .placements.variable_placer import VariablePlacer
from .placements.while_if_placer import WhileIfPlacer
from .placements.triangle_placer import TrianglePlacer
from .placements.zigzag_placer import ZigzagPlacer
from .placements.h_shape_placer import HShapePlacer
from .placements.ef_shape_placer import EFShapePlacer
from .placements.plus_shape_placer import PlusShapePlacer
from .placements.arrow_shape_placer import ArrowShapePlacer
from .placements.t_shape_placer import TShapePlacer
from src.map_generator.models.map_data import MapData

# --- Định nghĩa các chiến lược có sẵn ---
# Sổ đăng ký các chiến lược tạo hình dạng (Topology)
TOPOLOGIES = {
    "straight_line": StraightLineTopology(),
    "l_shape": LShapeTopology(),
    "u_shape": UShapeTopology(),
    "s_shape": SShapeTopology(),
    "zigzag": ZigzagTopology(),
    "triangle": TriangleTopology(),
    "h_shape": HShapeTopology(),
    "ef_shape": EFShapeTopology(),
    "plus_shape": PlusShapeTopology(),
    "arrow_shape": ArrowShapeTopology(),
    "t_shape": TShapeTopology()
}
# Sổ đăng ký các chiến lược đặt logic game (Placer)
PLACERS = {
    "sequencing": SequencingPlacer(),
    "for_loop": ForLoopPlacer(),
    "variable": VariablePlacer(),
    "while_if": WhileIfPlacer(),
    "zigzag": ZigzagPlacer(),
    "triangle": TrianglePlacer(),
    "h_shape": HShapePlacer(),
    "ef_shape": EFShapePlacer(),
    "plus_shape": PlusShapePlacer(),
    "arrow_shape": ArrowShapePlacer(),
    "t_shape": TShapePlacer()
}

class MapGenerator:
    """
    Lớp điều phối chính, chịu trách nhiệm lắp ráp một map hoàn chỉnh
    từ một Topology và một Placer.
    """
    def __init__(self, grid_size: tuple = (16, 16, 16)):
        """
        Khởi tạo MapGenerator.
        Args:
            grid_size (tuple): Kích thước mặc định của lưới map.
        """
        self.grid_size = grid_size
        print("⚙️  MapGenerator đã được khởi tạo.")

    def generate(self, map_type: str, logic_type: str, params: dict) -> MapData:
        """
        Hàm chính để sinh ra một đối tượng MapData hoàn chỉnh.

        Args:
            map_type (str): Tên của Topology cần sử dụng (ví dụ: 'zigzag').
            logic_type (str): Tên của Placer cần sử dụng (ví dụ: 'zigzag').
            params (dict): Các tham số tùy chỉnh cho việc sinh map.

        Returns:
            MapData: Một đối tượng chứa toàn bộ dữ liệu của map đã được sinh ra.
        """
        print(f"\n--- Bắt đầu sinh map: [Topology: '{map_type}', Placer: '{logic_type}'] ---")

        # 1. Chọn và chạy Topology để lấy thông tin đường đi thô
        topology_strategy = TOPOLOGIES.get(map_type)
        if not topology_strategy:
            raise ValueError(f"Không tìm thấy Topology nào có tên '{map_type}' đã được đăng ký.")
        path_info = topology_strategy.generate_path_info(self.grid_size, params)

        # 2. Chọn và chạy Placer để đặt logic game lên đường đi
        placement_strategy = PLACERS.get(logic_type)
        if not placement_strategy:
            raise ValueError(f"Không tìm thấy Placer nào có tên '{logic_type}' đã được đăng ký.")
        final_layout = placement_strategy.place_items(path_info, params)

        # 3. Đóng gói tất cả thông tin vào đối tượng MapData
        map_data = MapData(grid_size=self.grid_size, path_coords=path_info.path_coords, **final_layout)
        
        print(f"--- Hoàn thành sinh map: '{map_type}' với logic '{logic_type}' ---")
        return map_data
