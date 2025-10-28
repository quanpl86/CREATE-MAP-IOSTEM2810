# scripts/calculate_lines.py
import json 
import re
import sys
from typing import List

# ===================================================================
# HÀM TÍNH LLOC TỪ JS (DỰ PHÒNG – DÙNG TRONG generate_all_maps.py)
# ===================================================================
def calculate_logical_lines_py(js_code: str) -> int:
    """
    Tính LLOC từ chuỗi JavaScript sinh ra
    """
    if not js_code:
        return 0
    code = re.sub(r'/\*[\s\S]*?\*/|//.*', '', js_code)
    lines = [line.strip() for line in code.split('\n') if line.strip()]
    logical_lines = 0
    for line in lines:
        if line in ['{', '}']:
            continue
        if (line.endswith(';') or line.endswith('()') or 
            line.startswith('for (') or line.startswith('if (') or 
            line.startswith('while (') or line.startswith('function ') or 
            line.startswith('} else {') or re.match(r'^\w+\s*\(', line)):
            logical_lines += 1
    return logical_lines


# ===================================================================
# HÀM TÍNH LLOC CHỈ TỪ structuredSolution (CHÍNH XÁC 100%)
# ===================================================================
def calculate_optimal_lines_from_structured(program_dict: dict) -> int:
    """
    [REWRITTEN] Tính toán LLOC trực tiếp từ cấu trúc dictionary của chương trình.
    """
    def _count_lines_recursively(block_list: list, declared_vars: set) -> int:
        lloc = 0
        for block in block_list:
            block_type = block.get("type")
            if block_type == "variables_set":
                var_name = block.get("variable")
                if var_name and var_name not in declared_vars:
                    lloc += 1  # Đếm dòng 'var x;'
                    declared_vars.add(var_name)
                lloc += 1 # Đếm dòng 'x = ...;'
            elif block_type in ["maze_repeat", "maze_repeat_variable", "maze_repeat_expression"]:
                lloc += 1 # Đếm dòng 'for (...) {'
                # Đệ quy đếm các dòng bên trong vòng lặp
                lloc += _count_lines_recursively(block.get("body", []), declared_vars)
            elif block_type: # Các khối khác (move, turn, call, collect...)
                lloc += 1
        return lloc

    total_lloc = 0
    declared_variables = set()

    # Đếm các dòng trong các hàm
    for proc_name, proc_body in program_dict.get("procedures", {}).items():
        total_lloc += 1 # Đếm dòng 'function procName() {'
        total_lloc += _count_lines_recursively(proc_body, declared_variables)

    # Đếm các dòng trong chương trình chính
    main_body = program_dict.get("main", [])
    total_lloc += _count_lines_recursively(main_body, declared_variables)

    return total_lloc


# ===================================================================
# HÀM CHUYỂN structuredSolution → JS
# ===================================================================
def format_dict_to_string_list(program_dict: dict) -> List[str]:
    """
    [REWRITTEN] Tạo ra một list các dòng string để lưu vào JSON.
    Hàm này in rõ ràng các khối định nghĩa hàm và các loại vòng lặp khác nhau.
    """
    def _format_recursive(program_dict: dict, indent_level=0) -> List[str]:
        lines = []
        prefix = "  " * indent_level # noqa

        # In các khối định nghĩa hàm trước
        if indent_level == 0 and program_dict.get("procedures"):
            for name, body in program_dict["procedures"].items():
                lines.append(f"{prefix}DEFINE {name}:")
                lines.extend(_format_recursive({"body": body}, indent_level + 1))
            if program_dict.get("main"):
                lines.append("") # Thêm dòng trống ngăn cách

        # In chương trình chính
        if indent_level == 0:
            lines.append(f"{prefix}MAIN PROGRAM:")
            lines.append(f"{prefix}  On start:")
            body_to_print = program_dict.get("main", []) # noqa
            lines.extend(_format_recursive({"body": body_to_print}, indent_level + 2)) # Tăng indent
        else: # Đệ quy cho body của hàm/vòng lặp
            body_to_print = program_dict.get("body", [])
            for block in body_to_print:
                block_type = block.get("type")
                if block_type == 'maze_repeat':
                    lines.append(f"{prefix}repeat ({block.get('times', 1)}) do:")
                    lines.extend(_format_recursive(block, indent_level + 1))
                elif block_type == 'maze_repeat_variable':
                    lines.append(f"{prefix}repeat with variable ({block.get('variable', 'steps')}) do:")
                    lines.extend(_format_recursive(block, indent_level + 1))
                elif block_type == 'maze_repeat_expression':
                    lines.append(f"{prefix}repeat with expression do:")
                    lines.extend(_format_recursive(block, indent_level + 1))
                elif block_type == 'variables_set':
                    var_name = block.get('variable', 'item')
                    value = block.get('value', 0)
                    if isinstance(value, dict):
                        # Xử lý giá trị là một khối lồng nhau
                        value_str = f"value from block: {value.get('type')}"
                    else:
                        value_str = str(value)
                    lines.append(f"{prefix}set {var_name} to {value_str}")
                elif block_type == 'CALL':
                    lines.append(f"{prefix}CALL {block.get('name')}")
                elif block_type == 'maze_turn':
                    lines.append(f"{prefix}{block.get('direction', 'turn')}")
                else:
                    # Các khối đơn giản khác
                    lines.append(f"{prefix}{block_type}")
        return lines

    return _format_recursive(program_dict)

def format_program_for_json(program: dict) -> dict:
    """
    [REWRITTEN] Trả về chính cấu trúc dictionary của chương trình.
    Điều này giúp đồng bộ hóa dữ liệu và dễ dàng xử lý ở các bước sau.
    """
    return program

def translate_structured_solution_to_js(structured_solution: List[str], raw_actions: List[str] = None) -> str:
    if raw_actions is None:
        raw_actions = []
    turn_actions = [a for a in raw_actions if a in ['turnLeft', 'turnRight']]
    turn_idx = 0

    js_lines = []
    indent = 0
    variables = set()
    loop_counter = 0
    in_procedure = False

    i = 0
    while i < len(structured_solution):
        line = structured_solution[i]
        trimmed = line.strip()
        current_indent = (len(line) - len(line.lstrip())) // 2

        while indent > current_indent:
            js_lines.append("  " * indent + "}")
            indent -= 1

        if not trimmed:
            i += 1
            continue

        if trimmed == "MAIN PROGRAM:":
            in_procedure = False
            i += 1
            continue
        if trimmed.startswith("DEFINE PROCEDURE_"):
            proc_name = "procedure" + trimmed.split("_")[1].rstrip(":")
            js_lines.append(f"function {proc_name}() {{")
            indent += 1
            in_procedure = True
            i += 1
            continue
        if trimmed in {"On start:", "On start."}:
            i += 1
            continue

        if trimmed == "variables_set":
            js_lines.append("  " * indent + "var steps;")
            js_lines.append("  " * indent + "steps = 5;")
        elif trimmed.startswith("variables_set_to "):
            parts = trimmed.split(" ", 3)
            var_name = parts[2]
            value = parts[3] if len(parts) > 3 else "0"
            if var_name not in variables:
                js_lines.append("  " * indent + f"var {var_name};")
                variables.add(var_name)
            js_lines.append("  " * indent + f"{var_name} = {value};")
        elif trimmed == "maze_repeat_variable":
            var = f"count{loop_counter}"
            loop_counter += 1
            js_lines.append("  " * indent + f"for (var {var} = 0; {var} < steps; {var}++) {{")
            indent += 1
        elif trimmed.startswith("repeat ("):
            n = re.search(r"\d+", trimmed).group()
            var = f"count{loop_counter}"
            loop_counter += 1
            js_lines.append("  " * indent + f"for (var {var} = 0; {var} < {n}; {var}++) {{")
            indent += 1
        elif trimmed.startswith("while "):
            cond = trimmed.split(" ", 1)[1]
            js_lines.append("  " * indent + f"while ({cond}) {{")
            indent += 1
        elif trimmed.startswith("for "):
            js_lines.append("  " * indent + trimmed.replace("for ", "for (") + ") {")
            indent += 1
        elif trimmed.startswith("if "):
            cond = trimmed.split(" ", 1)[1]
            js_lines.append("  " * indent + f"if ({cond}) {{")
            indent += 1
        elif trimmed == "else":
            indent -= 1
            js_lines.append("  " * indent + "} else {")
            indent += 1
        elif trimmed.startswith("CALL PROCEDURE_"):
            proc = "procedure" + trimmed.split("_")[1]
            js_lines.append("  " * indent + f"{proc}();")
        elif trimmed in {"moveForward", "collect", "jump"}:
            func = {"moveForward": "moveForward", "collect": "collectItem", "jump": "jump"}[trimmed]
            js_lines.append("  " * indent + f"{func}();")
        elif trimmed.startswith("maze_turn"):
            turn = turn_actions[turn_idx] if turn_idx < len(turn_actions) else "turnRight"
            js_lines.append("  " * indent + f"{turn}();")
            turn_idx += 1
        elif re.match(r"^\w+ = .+", trimmed):
            js_lines.append("  " * indent + trimmed + ";")
        elif re.match(r"^\w+ [+*/-]= .+", trimmed):
            js_lines.append("  " * indent + trimmed + ";")
        elif trimmed.startswith("math_"):
            js_lines.append("  " * indent + trimmed.replace("math_", "Math.") + ";")
        elif trimmed.startswith("logic_"):
            js_lines.append("  " * indent + trimmed.replace("logic_", "") + ";")

        i += 1

    while indent > 0:
        js_lines.append("  " * indent + "}")
        indent -= 1

    return "\n".join(js_lines)


# ===================================================================
# MAIN: CHẠY ĐỘC LẬP
# ===================================================================
def main():
    if len(sys.argv) != 2:
        print("Usage: python calculate_lines.py <path_to_solution.json>", file=sys.stderr)
        sys.exit(1)

    filepath = sys.argv[1]
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        structured = data.get("structuredSolution", [])
        raw_actions = data.get("rawActions", [])

        # Tính LLOC từ structuredSolution (ưu tiên)
        lloc = calculate_optimal_lines_from_structured(structured)
        print("=== optimalLines (từ structuredSolution) ===")
        print(lloc)

        # (Tùy chọn) Tính từ JS
        js_code = translate_structured_solution_to_js(structured, raw_actions)
        lloc_js = calculate_logical_lines_py(js_code)
        print("\n=== LLOC từ JS (để kiểm tra) ===")
        print(lloc_js)

        print("\n=== JS SINH RA ===")
        print(js_code)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()