# src/bug_generator/strategies/main_thread_bugs.py
import random
from typing import Any, Dict, List
from .base_strategy import BaseBugStrategy

def _find_blocks_recursively(program_part: List[Dict], condition: callable) -> List[Dict]:
    """Hàm helper để tìm tất cả các khối thỏa mãn một điều kiện trong cấu trúc chương trình."""
    found_blocks = []
    for block in program_part:
        if condition(block):
            found_blocks.append(block)
        # Đệ quy vào các khối lồng nhau (vòng lặp, hàm)
        if "body" in block and isinstance(block["body"], list):
            found_blocks.extend(_find_blocks_recursively(block["body"], condition))
    return found_blocks

class MisplacedBlocksBug(BaseBugStrategy):
    """
    1.1. Lỗi Tuần Tự: Sai Thứ Tự Khối Lệnh (Sequence Error)
    Hoán đổi vị trí của hai khối lệnh ngẫu nhiên trong chương trình chính.
    """
    def apply(self, program_dict: Dict[str, Any], config: Dict) -> Dict[str, Any]:
        main_body = program_dict.get("main", [])
        if len(main_body) >= 2:
            # Chỉ hoán đổi các khối ở cấp cao nhất của chương trình chính
            idx1, idx2 = random.sample(range(len(main_body)), 2)
            main_body[idx1], main_body[idx2] = main_body[idx2], main_body[idx1]
            print(f"      -> Bug 'sequence_error': Hoán đổi khối lệnh ở vị trí {idx1} và {idx2} trong main.")
        else:
            print("   - ⚠️ Không đủ khối lệnh trong main để tạo lỗi 'sequence_error'.")
        return program_dict

class MissingBlockBug(BaseBugStrategy):
    """
    1.1. Lỗi Tuần Tự: Thiếu Khối Lệnh (Missing Block Error)
    Xóa một khối lệnh ngẫu nhiên.
    """
    def apply(self, program_dict: Dict[str, Any], config: Dict) -> Dict[str, Any]:
        all_bodies = [program_dict.get("main", [])]
        for proc_body in program_dict.get("procedures", {}).values():
            all_bodies.append(proc_body)

        # Tìm tất cả các "body" (danh sách các khối) có thể xóa được
        possible_bodies_to_modify = [body for body in all_bodies if len(body) > 1]

        if possible_bodies_to_modify:
            target_body = random.choice(possible_bodies_to_modify)
            # Ưu tiên xóa các khối đơn giản (không phải vòng lặp/hàm)
            simple_blocks_indices = [
                i for i, block in enumerate(target_body)
                if "body" not in block and block.get("type") != "CALL"
            ]
            if simple_blocks_indices:
                remove_idx = random.choice(simple_blocks_indices)
            else:
                remove_idx = random.randint(0, len(target_body) - 1)
            
            removed_block = target_body.pop(remove_idx)
            print(f"      -> Bug 'missing_block': Đã xóa khối '{removed_block.get('type')}'")
        else:
            print("   - ⚠️ Không tìm thấy nơi nào phù hợp để xóa khối lệnh.")
        return program_dict

class IncorrectLoopCountBug(BaseBugStrategy):
    """
    1.2. Lỗi Cấu Hình: Sai Số Lần Lặp (Incorrect Loop Count)
    """
    def apply(self, program_dict: Dict[str, Any], config: Dict) -> Dict[str, Any]:
        # Tìm tất cả các khối vòng lặp trong toàn bộ chương trình
        all_loops = _find_blocks_recursively(
            program_dict.get("main", []),
            lambda block: block.get("type") == "maze_repeat"
        )
        for proc_body in program_dict.get("procedures", {}).values():
            all_loops.extend(_find_blocks_recursively(
                proc_body,
                lambda block: block.get("type") == "maze_repeat"
            ))

        if all_loops:
            target_loop = random.choice(all_loops)
            original_num = target_loop.get("times", 1)
            # Tạo lỗi: +1 hoặc -1, đảm bảo không nhỏ hơn 1
            offset = random.choice([-1, 1])
            bugged_num = original_num + offset
            if bugged_num <= 0:
                bugged_num = original_num + 1 # Nếu trừ đi bị <= 0 thì cộng
            
            target_loop["times"] = bugged_num
            print(f"      -> Bug 'incorrect_loop_count': Thay đổi số lần lặp từ {original_num} thành {bugged_num}.")
        else:
            print("   - ⚠️ Không tìm thấy khối 'maze_repeat' để tạo lỗi.")
        return program_dict

class IncorrectParameterBug(BaseBugStrategy):
    """
    1.2. Lỗi Cấu Hình: Sai Tham Số (Incorrect Parameter)
    Ví dụ: rẽ sai hướng.
    """
    def apply(self, program_dict: Dict[str, Any], config: Dict) -> Dict[str, Any]:
        # Tìm tất cả các khối rẽ
        all_turns = _find_blocks_recursively(
            program_dict.get("main", []),
            lambda block: block.get("type") == "maze_turn"
        )
        for proc_body in program_dict.get("procedures", {}).values():
            all_turns.extend(_find_blocks_recursively(
                proc_body,
                lambda block: block.get("type") == "maze_turn"
            ))

        if all_turns:
            target_turn = random.choice(all_turns)
            original_dir = target_turn.get("direction", "turnRight") # Giả định mặc định là Right
            bugged_dir = "turnLeft" if original_dir == "turnRight" else "turnRight"
            target_turn["direction"] = bugged_dir
            print(f"      -> Bug 'incorrect_parameter': Thay đổi hướng rẽ từ {original_dir} thành {bugged_dir}.")
        else:
            print("   - ⚠️ Không tìm thấy khối 'maze_turn' để tạo lỗi incorrect_parameter.")
        return program_dict

class IncorrectMathExpressionBug(BaseBugStrategy):
    """
    1.3. Lỗi Dữ Liệu: Sai Biểu Thức Toán Học (Incorrect Math Expression)
    Thay đổi toán tử trong một khối `math_arithmetic`.
    """
    def apply(self, program_dict: Dict[str, Any], config: Dict) -> Dict[str, Any]:
        # Tìm tất cả các khối có chứa biểu thức toán học
        # Trong trường hợp này, nó nằm trong 'maze_repeat_expression'
        math_expr_blocks = _find_blocks_recursively(
            program_dict.get("main", []),
            lambda block: block.get("type") == "maze_repeat_expression"
        )
        for proc_body in program_dict.get("procedures", {}).values():
            math_expr_blocks.extend(_find_blocks_recursively(
                proc_body,
                lambda block: block.get("type") == "maze_repeat_expression"
            ))

        if math_expr_blocks:
            target_block = random.choice(math_expr_blocks)
            expression = target_block.get("expression")
            if expression and expression.get("type") == "math_arithmetic":
                original_op = expression.get("op", "ADD")
                # Chọn một toán tử khác để thay thế
                possible_ops = ["ADD", "SUBTRACT", "MULTIPLY", "DIVIDE"]
                possible_ops.remove(original_op)
                bugged_op = random.choice(possible_ops)
                expression["op"] = bugged_op
                print(f"      -> Bug 'incorrect_math_expression': Thay đổi toán tử từ {original_op} thành {bugged_op}.")
        else:
            print("   - ⚠️ Không tìm thấy khối 'maze_repeat_expression' để tạo lỗi.")
        return program_dict

class IncorrectInitialValueBug(BaseBugStrategy):
    """
    1.3. Lỗi Dữ Liệu: Sai Giá Trị Khởi Tạo (Incorrect Initial Value)
    Tìm một khối `variables_set` và thay đổi giá trị số của nó.
    """
    def apply(self, program_dict: Dict[str, Any], config: Dict) -> Dict[str, Any]:
        # Tìm tất cả các khối gán giá trị là một số
        set_var_blocks = _find_blocks_recursively(
            program_dict.get("main", []),
            lambda block: (
                block.get("type") == "variables_set" and
                isinstance(block.get("value"), int)
            )
        )

        if set_var_blocks:
            target_block = random.choice(set_var_blocks)
            original_value = target_block["value"]
            # Tạo lỗi: +1 hoặc -1, đảm bảo không nhỏ hơn 1
            offset = random.choice([-1, 1])
            bugged_value = original_value + offset
            if bugged_value <= 0:
                bugged_value = original_value + 1
            
            target_block["value"] = bugged_value
            print(f"      -> Bug 'incorrect_initial_value': Thay đổi giá trị khởi tạo của biến '{target_block.get('variable')}' từ {original_value} thành {bugged_value}.")
        else:
            print("   - ⚠️ Không tìm thấy khối 'variables_set' với giá trị số để tạo lỗi.")
        return program_dict

class WrongLogicInAlgorithmBug(BaseBugStrategy):
    """
    Lỗi logic trong một thuật toán phức tạp (ví dụ: Fibonacci).
    Thay đổi các biến trong phép toán để làm sai logic.
    """
    def apply(self, program_dict: Dict[str, Any], config: Dict) -> Dict[str, Any]:
        # Tìm khối tính toán Fibonacci: b = temp + b
        fibonacci_calc_blocks = _find_blocks_recursively(
            program_dict.get("main", []),
            lambda block: (
                block.get("type") == "variables_set" and
                isinstance(block.get("value"), dict) and
                block["value"].get("type") == "math_arithmetic" and
                block["value"].get("op") == "ADD"
            )
        )

        if fibonacci_calc_blocks:
            target_block = fibonacci_calc_blocks[0] # Giả định chỉ có 1 khối
            math_expr = target_block["value"]
            original_vars = (math_expr.get("var_a"), math_expr.get("var_b"))

            # Tạo lỗi: thay vì b = temp + b, ta đổi thành b = temp + a
            # Giả định var_a là 'temp' và var_b là 'b'
            if original_vars[0] and original_vars[1]:
                math_expr["var_b"] = original_vars[0] # Đổi var_b thành var_a
                print(f"      -> Bug 'wrong_logic_in_algorithm': Thay đổi phép toán từ "
                      f"'{original_vars[0]} + {original_vars[1]}' thành "
                      f"'{math_expr['var_a']} + {math_expr['var_b']}'.")
        else:
            print("   - ⚠️ Không tìm thấy khối tính toán thuật toán phù hợp để tạo lỗi.")
        return program_dict

class RedundantBlocksBug(BaseBugStrategy):
    """
    1.4. Lỗi Tối Ưu Hóa: Thừa Khối Lệnh (Redundant Blocks)
    """
    def apply(self, actions: List[str], config: Dict) -> List[str]:
        if not actions: return actions
        insert_idx = random.randint(0, len(actions))
        actions.insert(insert_idx, 'turnRight')
        actions.insert(insert_idx, 'turnLeft')
        print(f"      -> Bug 'optimization': Chèn cặp lệnh rẽ thừa ở vị trí {insert_idx}.")
        return actions
