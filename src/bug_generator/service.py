# src/bug_generator/service.py
from typing import Dict, Any, Type
import copy

# --- SECTION 1: Import các chiến lược tạo lỗi ---
# Import các lớp chiến lược đã được tổ chức lại
from .strategies.base_strategy import BaseBugStrategy
from .strategies.main_thread_bugs import (
    MisplacedBlocksBug,
    MissingBlockBug,
    IncorrectLoopCountBug, IncorrectInitialValueBug,
    IncorrectParameterBug, IncorrectMathExpressionBug,
    WrongLogicInAlgorithmBug, # [MỚI] Import chiến lược lỗi thuật toán
    RedundantBlocksBug,
    # Thêm các lớp khác khi bạn tạo chúng, ví dụ:
    # IncorrectInitialValueBug,
    # IncorrectMathOperatorBug,
)
# from .strategies.function_bugs import (
#     IncorrectFunctionLogicBug,
#     MissingFunctionCallBug,
# )

# --- SECTION 2: Nhà máy tạo lỗi (Bug Strategy Factory) ---
# Ánh xạ bug_type tới lớp chiến lược tương ứng.
# Cấu trúc này tuân theo bản phân loại chi tiết của bạn.
BUG_STRATEGIES: Dict[str, Type[BaseBugStrategy]] = {
    # Nhóm 1.1: Lỗi Tuần Tự và Cấu Trúc Cơ Bản
    'sequence_error': MisplacedBlocksBug,
    'missing_block': MissingBlockBug,
    # 'misplaced_control_structure': # Sẽ thêm lớp này sau
    
    # Nhóm 1.2: Lỗi Cấu Hình Khối Điều Khiển
    'incorrect_loop_count': IncorrectLoopCountBug,
    'incorrect_parameter': IncorrectParameterBug, # Ví dụ: sai hướng rẽ
    'incorrect_block': IncorrectParameterBug, # [MỚI] Thêm alias cho bug rẽ sai hướng
    # 'incorrect_loop_condition': # Sẽ thêm lớp này sau
    
    # Nhóm 1.3: Lỗi Dữ Liệu và Tính Toán    
    'incorrect_initial_value': IncorrectInitialValueBug,
    # 'missing_variable_update': MissingBlockBug, # Có thể dùng lại MissingBlockBug để xóa khối 'change'
    'incorrect_math_expression': IncorrectMathExpressionBug,
    'wrong_logic_in_algorithm': WrongLogicInAlgorithmBug, # [MỚI] Đăng ký chiến lược
    
    # Nhóm 1.4: Lỗi Tối Ưu Hóa
    'optimization': RedundantBlocksBug,
    
    # Nhóm 2.1: Lỗi Bên Trong Hàm
    # 'incorrect_logic_in_function': IncorrectFunctionLogicBug,
    
    # Nhóm 2.2: Lỗi Gọi Hàm
    'incorrect_function_call_order': MisplacedBlocksBug, # Dùng lại logic hoán đổi khối
    # 'missing_function_call': MissingBlockBug, # Dùng lại logic xóa khối
}

# --- SECTION 3: Hàm điều phối chính (Dispatcher) ---
def create_bug(bug_type: str, data: Any, config: Dict = None) -> Any:
    """
    Hàm điều phối chính. Tìm chiến lược phù hợp, khởi tạo và áp dụng nó.
    """
    config = config or {}
    strategy_class = BUG_STRATEGIES.get(bug_type)

    # [REWRITTEN] Logic mới làm việc với dictionary
    if strategy_class and isinstance(data, dict):
        print(f"    LOG: Đang tạo lỗi loại '{bug_type}'.")
        # Tạo một bản sao sâu để đảm bảo không làm thay đổi lời giải gốc
        program_copy = copy.deepcopy(data)
        
        # Khởi tạo và áp dụng chiến lược
        strategy_instance = strategy_class()
        return strategy_instance.apply(program_copy, config)
    else:
        if not isinstance(data, dict):
            print(f"    - ⚠️ Cảnh báo: Dữ liệu đầu vào cho create_bug không phải là dictionary. Bug type: '{bug_type}'.")
        else:
            print(f"    - ⚠️ Cảnh báo: Không tìm thấy chiến lược tạo lỗi cho loại '{bug_type}'. Trả về dữ liệu gốc.")
        return data