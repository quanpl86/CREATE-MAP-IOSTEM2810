# scripts/generate_all_maps.py

import json
import os
import copy # Import module copy
import sys
import random

# --- Thiết lập đường dẫn để import từ thư mục src ---
# Lấy đường dẫn đến thư mục gốc của dự án (đi lên 2 cấp từ file hiện tại)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Thêm thư mục src vào sys.path để Python có thể tìm thấy các module
SRC_PATH = os.path.join(PROJECT_ROOT, 'src')
if SRC_PATH not in sys.path:
    sys.path.append(SRC_PATH)
# ----------------------------------------------------

# Bây giờ chúng ta có thể import từ src một cách an toàn
from map_generator.service import MapGeneratorService
from scripts.gameSolver import solve_map_and_get_solution
from bug_generator.service import create_bug # [THAY ĐỔI] Import hàm điều phối mới
# --- [MỚI] Tích hợp tính năng tính toán số dòng code ---
# Import các hàm cần thiết trực tiếp từ calculate_lines.py
from scripts.calculate_lines import (
    calculate_logical_lines_py,
    translate_structured_solution_to_js,
    calculate_optimal_lines_from_structured, # noqa
    format_dict_to_string_list
)
# ---------------------------------------------------------
import re
import xml.etree.ElementTree as ET

def actions_to_xml(actions: list) -> str:
    """Chuyển đổi danh sách hành động thành chuỗi XML lồng nhau cho Blockly."""
    if not actions:
        return ""
    
    action = actions[0]
    # Đệ quy tạo chuỗi cho các khối còn lại
    next_block_xml = actions_to_xml(actions[1:])
    next_tag = f"<next>{next_block_xml}</next>" if next_block_xml else ""

    if action == 'turnLeft' or action == 'turnRight':
        direction = 'turnLeft' if action == 'turnLeft' else 'turnRight'
        return f'<block type="maze_turn"><field name="DIR">{direction}</field>{next_tag}</block>'
    
    # Các action khác như moveForward, jump, collect, toggleSwitch
    action_name = action.replace("maze_", "")
    return f'<block type="maze_{action_name}">{next_tag}</block>'

def _create_xml_from_structured_solution(program_dict: dict, raw_actions: list = None) -> str:
    """
    [REWRITTEN] Chuyển đổi dictionary lời giải thành chuỗi XML Blockly một cách an toàn.
    Sử dụng ElementTree để xây dựng cây XML thay vì xử lý chuỗi.
    [IMPROVED] Nhận thêm `raw_actions` để xác định hướng rẽ chính xác.
    """
    # [MỚI] Tạo một iterator cho các hành động rẽ từ raw_actions
    # để có thể lấy tuần tự khi cần.
    if raw_actions is None:
        raw_actions = []
    turn_actions_iterator = iter([a for a in raw_actions if a in ['turnLeft', 'turnRight']])

    def build_blocks_recursively(block_list: list) -> list[ET.Element]:
        """Hàm đệ quy để xây dựng một danh sách các đối tượng ET.Element từ dict."""
        elements = []
        for block_data in block_list:
            block_type = block_data.get("type")
            block_element = None # Khởi tạo là None
            
            if block_type == "CALL":
                # [SỬA] Xử lý khối gọi hàm
                block_element = ET.Element('block', {'type': 'procedures_callnoreturn'})
                ET.SubElement(block_element, 'mutation', {'name': block_data.get("name")})
            elif block_type == "maze_repeat":
                block_element = ET.Element('block', {'type': 'maze_repeat'})
                value_el = ET.SubElement(block_element, 'value', {'name': 'TIMES'})
                shadow_el = ET.SubElement(value_el, 'shadow', {'type': 'math_number'})
                field_el = ET.SubElement(shadow_el, 'field', {'name': 'NUM'})
                field_el.text = str(block_data.get("times", 1))
                
                statement_el = ET.SubElement(block_element, 'statement', {'name': 'DO'})
                inner_blocks = build_blocks_recursively(block_data.get("body", []))
                if inner_blocks:
                    # Nối các khối bên trong statement lại với nhau
                    for i in range(len(inner_blocks) - 1):
                        ET.SubElement(inner_blocks[i], 'next').append(inner_blocks[i+1])
                    statement_el.append(inner_blocks[0])
            elif block_type == "variables_set":
                block_element = ET.Element('block', {'type': 'variables_set'})
                field_var = ET.SubElement(block_element, 'field', {'name': 'VAR'})
                field_var.text = block_data.get("variable", "item")
                
                value_el = ET.SubElement(block_element, 'value', {'name': 'VALUE'})
                # [FIX] Xử lý giá trị có thể là một khối khác (variables_get, math_arithmetic)
                value_content = block_data.get("value", 0)
                if isinstance(value_content, dict): # Nếu giá trị là một khối lồng nhau
                    nested_value_blocks = build_blocks_recursively([value_content])
                    if nested_value_blocks:
                        value_el.append(nested_value_blocks[0])
                else: # Nếu giá trị là một số đơn giản
                    shadow_el = ET.SubElement(value_el, 'shadow', {'type': 'math_number'})
                    field_num = ET.SubElement(shadow_el, 'field', {'name': 'NUM'})
                    field_num.text = str(value_content)
            elif block_type == "maze_repeat_variable":
                block_element = ET.Element('block', {'type': 'maze_repeat'})
                value_el = ET.SubElement(block_element, 'value', {'name': 'TIMES'})
                # Thay vì shadow, chúng ta tạo một khối variables_get
                var_get_el = ET.SubElement(value_el, 'block', {'type': 'variables_get'})
                field_var = ET.SubElement(var_get_el, 'field', {'name': 'VAR'})
                field_var.text = block_data.get("variable", "item")
                statement_el = ET.SubElement(block_element, 'statement', {'name': 'DO'})
                inner_blocks = build_blocks_recursively(block_data.get("body", []))
                if inner_blocks:
                    statement_el.append(inner_blocks[0])
            elif block_type == "maze_repeat_expression":
                block_element = ET.Element('block', {'type': 'maze_repeat'})
                value_el = ET.SubElement(block_element, 'value', {'name': 'TIMES'})
                # Tạo khối biểu thức toán học
                expr_data = block_data.get("expression", {})
                math_block = ET.SubElement(value_el, 'block', {'type': expr_data.get("type", "math_arithmetic")})
                ET.SubElement(math_block, 'field', {'name': 'OP'}).text = expr_data.get("op", "ADD")
                # Input A
                val_a = ET.SubElement(math_block, 'value', {'name': 'A'})
                var_a_block = ET.SubElement(val_a, 'block', {'type': 'variables_get'})
                ET.SubElement(var_a_block, 'field', {'name': 'VAR'}).text = expr_data.get("var_a", "a")
                # Input B
                val_b = ET.SubElement(math_block, 'value', {'name': 'B'})
                var_b_block = ET.SubElement(val_b, 'block', {'type': 'variables_get'})
                ET.SubElement(var_b_block, 'field', {'name': 'VAR'}).text = expr_data.get("var_b", "b")

                statement_el = ET.SubElement(block_element, 'statement', {'name': 'DO'})
                inner_blocks = build_blocks_recursively(block_data.get("body", []))
                if inner_blocks:
                    statement_el.append(inner_blocks[0])
            elif block_type == "variables_get":
                # [SỬA LỖI] Xử lý tường minh khối variables_get
                block_element = ET.Element('block', {'type': 'variables_get'})
                field_var = ET.SubElement(block_element, 'field', {'name': 'VAR'})
                field_var.text = block_data.get("variable", "item")
            elif block_type == "math_arithmetic":
                # [SỬA LỖI] Xử lý tường minh khối math_arithmetic
                block_element = ET.Element('block', {'type': 'math_arithmetic'})
                ET.SubElement(block_element, 'field', {'name': 'OP'}).text = block_data.get("op", "ADD")
                # Input A
                val_a_el = ET.SubElement(block_element, 'value', {'name': 'A'})
                var_a_block = ET.SubElement(val_a_el, 'block', {'type': 'variables_get'})
                ET.SubElement(var_a_block, 'field', {'name': 'VAR'}).text = block_data.get("var_a", "a")
                # Input B
                val_b_el = ET.SubElement(block_element, 'value', {'name': 'B'})
                var_b_block = ET.SubElement(val_b_el, 'block', {'type': 'variables_get'})
                ET.SubElement(var_b_block, 'field', {'name': 'VAR'}).text = block_data.get("var_b", "b")
            else:
                # [SỬA] Xử lý các khối đơn giản khác
                action = block_type.replace("maze_", "") if block_type.startswith("maze_") else block_type
                # Blockly không có khối maze_collect, chỉ có maze_collect
                if action == "collect":
                    block_element = ET.Element('block', {'type': 'maze_collect'})
                elif action == "toggleSwitch":
                    block_element = ET.Element('block', {'type': 'maze_toggle_switch'})
                else:
                    block_element = ET.Element('block', {'type': f'maze_{action}'})

                if action == "turn":
                    # [FIX] Lấy hướng rẽ từ iterator, nếu hết thì dùng giá trị mặc định.
                    # Điều này đảm bảo XML sinh ra khớp với lời giải.
                    direction = next(turn_actions_iterator, "turnRight")
                    # Ghi đè lại nếu trong dict có sẵn thông tin direction (cho trường hợp bug)
                    direction = block_data.get("direction", direction)
                    field_el = ET.SubElement(block_element, 'field', {'name': 'DIR'})
                    field_el.text = direction
            
            if block_element is not None:
                elements.append(block_element)
        return elements
    
    # --- [SỬA LỖI] Logic mới để xử lý cả hàm và chương trình chính ---
    # Sẽ trả về một dictionary chứa các khối định nghĩa và khối main riêng biệt.
    final_xml_components = {"procedures": [], "main": None}
    
    # 1. Xử lý các khối định nghĩa hàm (procedures)
    for proc_name, proc_body in program_dict.get("procedures", {}).items():
        # [SỬA] Thêm deletable="false" và bỏ x, y
        proc_def_block = ET.Element('block', {'type': 'procedures_defnoreturn', 'deletable': 'false'})
        
        field_el = ET.SubElement(proc_def_block, 'field', {'name': 'NAME'})
        field_el.text = proc_name
        
        statement_el = ET.SubElement(proc_def_block, 'statement', {'name': 'STACK'})
        inner_blocks = build_blocks_recursively(proc_body)
        if inner_blocks:
            for i in range(len(inner_blocks) - 1):
                ET.SubElement(inner_blocks[i], 'next').append(inner_blocks[i+1])
            statement_el.append(inner_blocks[0])
        
        final_xml_components["procedures"].append(ET.tostring(proc_def_block, encoding='unicode'))

    # 2. Xử lý chương trình chính (main)
    main_blocks = build_blocks_recursively(program_dict.get("main", []))
    if main_blocks:
        for i in range(len(main_blocks) - 1):
            ET.SubElement(main_blocks[i], 'next').append(main_blocks[i+1])
        final_xml_components["main"] = ET.tostring(main_blocks[0], encoding='unicode')

    # [FIX] Nối tất cả các thành phần XML lại với nhau một cách chính xác.
    # Các khối định nghĩa hàm phải được đặt ở cấp cao nhất, bên ngoài khối maze_start.
    proc_defs_xml = "".join(final_xml_components["procedures"])
    main_code_xml = final_xml_components["main"] or ""

    # Bọc code chính trong khối maze_start
    # [FIX] Khối maze_start không nên có deletable="false" hoặc movable="false" ở đây,
    # vì nó sẽ được bọc trong thẻ <xml> và các thuộc tính đó áp dụng cho khối gốc.
    # Thay vào đó, ta sẽ thêm các thuộc tính này vào khối định nghĩa hàm.
    main_start_block = ET.Element('block', {'type': 'maze_start', 'deletable': 'false', 'movable': 'false'})
    main_statement = ET.SubElement(main_start_block, 'statement', {'name': 'DO'})
    if main_code_xml:
        # Phải parse lại chuỗi XML của main để append nó vào statement
        main_statement.append(ET.fromstring(main_code_xml))

    return proc_defs_xml + ET.tostring(main_start_block, encoding='unicode')

def main():
    """
    Hàm chính để chạy toàn bộ quy trình sinh map.
    Nó đọc file curriculum, sau đó gọi MapGeneratorService để tạo các file map tương ứng.
    """
    print("=============================================")
    print("=== BẮT ĐẦU QUY TRÌNH SINH MAP TỰ ĐỘNG ===")
    print("=============================================")

    # Xác định các đường dẫn file dựa trên thư mục gốc của dự án
    # [MỚI] Dictionary để ánh xạ tên topic VI sang EN
    # Trong tương lai, nên đưa thông tin này vào file curriculum_source.xlsx
    TOPIC_TRANSLATIONS = {
        "Giới thiệu": "Introduction",
        "Vòng lặp": "Loops",
        "Hàm": "Functions",
        "Biến & Toán học": "Variables & Math",
        "Gỡ lỗi": "Debugging",
        "Gỡ lỗi Nâng cao": "Advanced Debugging",
        "Hàm Nâng Cao": "Advanced Functions"
    }

    curriculum_dir = os.path.join(PROJECT_ROOT, 'data', 'curriculum')
    toolbox_filepath = os.path.join(PROJECT_ROOT, 'data', 'toolbox_presets.json')
    base_maps_output_dir = os.path.join(PROJECT_ROOT, 'data', 'base_maps') # Thư mục mới để test map
    final_output_dir = os.path.join(PROJECT_ROOT, 'data', 'final_game_levels')

    # --- Bước 1: [CẢI TIẾN] Lấy danh sách các file curriculum topic ---
    try:
        # Lọc ra tất cả các file có đuôi .json trong thư mục curriculum
        topic_files = sorted([f for f in os.listdir(curriculum_dir) if f.endswith('.json')])
        if not topic_files:
            print(f"❌ Lỗi: Không tìm thấy file curriculum nào trong '{curriculum_dir}'. Dừng chương trình.")
            return
        print(f"✅ Tìm thấy {len(topic_files)} file curriculum trong thư mục: {curriculum_dir}")
    except FileNotFoundError:
        print(f"❌ Lỗi: Không tìm thấy thư mục curriculum tại '{curriculum_dir}'. Dừng chương trình.")
        return

    # --- [MỚI] Đọc file cấu hình toolbox ---
    try:
        with open(toolbox_filepath, 'r', encoding='utf-8') as f:
            toolbox_presets = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        print(f"   ⚠️ Cảnh báo: Không tìm thấy hoặc file toolbox_presets.json không hợp lệ. Sẽ sử dụng toolbox rỗng.")
        toolbox_presets = {}

    # --- [SỬA LỖI] Đảm bảo thư mục đầu ra tồn tại trước khi ghi file ---
    if not os.path.exists(final_output_dir):
        os.makedirs(final_output_dir)
        print(f"✅ Đã tạo thư mục đầu ra: {final_output_dir}")
    if not os.path.exists(base_maps_output_dir):
        os.makedirs(base_maps_output_dir)
        print(f"✅ Đã tạo thư mục đầu ra cho map test: {base_maps_output_dir}")

    # --- Bước 2: Khởi tạo service sinh map ---
    map_generator = MapGeneratorService()
    
    total_maps_generated = 0
    total_maps_failed = 0

    # --- Bước 3: Lặp qua từng topic và từng yêu cầu map ---
    for topic_filename in topic_files:
        topic_filepath = os.path.join(curriculum_dir, topic_filename)
        try:
            with open(topic_filepath, 'r', encoding='utf-8') as f:
                topic = json.load(f)
            topic_code = topic.get('topic_code', 'UNKNOWN_TOPIC')
            topic_name_vi = topic.get('topic_name', 'N/A')
            print(f"\n>> Đang xử lý Topic: {topic_name_vi} ({topic_code}) từ file '{topic_filename}'")
        except json.JSONDecodeError:
            print(f"   ❌ Lỗi: File '{topic_filename}' không phải là file JSON hợp lệ. Bỏ qua topic này.")
            total_maps_failed += len(topic.get('suggested_maps', [])) # Giả định lỗi cho tất cả map trong file
            continue
        except Exception as e:
            print(f"   ❌ Lỗi không xác định khi đọc file '{topic_filename}': {e}. Bỏ qua topic này.")
            continue
        
        # SỬA LỖI: Sử dụng enumerate để lấy chỉ số của mỗi yêu cầu
        for request_index, map_request in enumerate(topic.get('suggested_maps', [])):
            # Lấy thông tin từ cấu trúc mới
            generation_config = map_request.get('generation_config', {})
            map_type = generation_config.get('map_type')
            logic_type = generation_config.get('logic_type')
            num_variants = generation_config.get('num_variants', 1)

            if not map_type or not logic_type:
                print(f"   ⚠️ Cảnh báo: Bỏ qua yêu cầu #{request_index + 1} trong topic {topic_code} vì thiếu 'map_type' hoặc 'logic_type'.")
                continue
            
            print(f"  -> Chuẩn bị sinh {num_variants} biến thể cho Yêu cầu '{map_request.get('id', 'N/A')}'")

            # Lặp để tạo ra số lượng biến thể mong muốn
            for variant_index in range(num_variants):
                try:
                    # --- Bước 4: Sinh map và tạo gameConfig ---
                    base_params = generation_config.get('params', {})
                    params_for_generation = copy.deepcopy(base_params)

                    # [CẢI TIẾN] Xử lý params động cho các biến thể.
                    # Nếu một giá trị trong params là một mảng, hãy chọn giá trị
                    # tương ứng với chỉ số của biến thể hiện tại.
                    for key, value in base_params.items():
                        if isinstance(value, list):
                            # Đảm bảo index không vượt quá độ dài của mảng
                            if variant_index < len(value):
                                params_for_generation[key] = value[variant_index]
                                print(f"    LOG: Biến thể {variant_index + 1}, sử dụng '{key}': {value[variant_index]}")
                            else:
                                # Nếu index vượt quá, dùng giá trị cuối cùng của mảng
                                params_for_generation[key] = value[-1]
                                print(f"    LOG: Biến thể {variant_index + 1}, index vượt quá, sử dụng giá trị cuối của '{key}': {value[-1]}")
                    
                    generated_map = map_generator.generate_map(
                        map_type=map_type,
                        logic_type=logic_type,
                        params=params_for_generation
                    )
                    
                    if not generated_map: continue

                    game_config = generated_map.to_game_engine_dict()

                    # [CẢI TIẾN] Đọc theme từ params để sử dụng cho vật cản
                    asset_theme = params_for_generation.get('asset_theme', {})
                    default_obstacle_model = asset_theme.get('obstacle', 'wall.brick01')
                    stair_model = asset_theme.get('stair', 'ground.checker')

                    # [REFACTORED] Bổ sung danh sách obstacles vào gameConfig.
                    # Bước này đảm bảo solver có thể nhận diện được chúng.
                    if generated_map.obstacles:
                        # [REFACTORED] Thống nhất type là "obstacle" và truyền modelKey nếu có.
                        # [CẢI TIẾN] Sử dụng modelKey từ theme làm mặc định.
                        game_config['gameConfig']['obstacles'] = [{"id": f"o{i+1}", "type": "obstacle", "modelKey": obs.get('modelKey', default_obstacle_model), "position": {"x": obs['pos'][0], "y": obs['pos'][1]+1, "z": obs['pos'][2]}} for i, obs in enumerate(generated_map.obstacles)]

                    # Bổ sung các khối vật lý của vật cản vào `blocks`
                    # để solver có thể nhận diện chúng là các khối vật lý có thể đứng lên được.
                    if generated_map.obstacles:
                         for obs in generated_map.obstacles:
                            y_offset = 0 if map_type in ['stepped_island_clusters', 'hub_with_stepped_islands'] else 1
                            model_key = obs.get('modelKey', default_obstacle_model) # Sử dụng modelKey từ theme
                            game_config['gameConfig']['blocks'].append({ "modelKey": model_key, "position": {"x": obs['pos'][0], "y": obs['pos'][1] + y_offset, "z": obs['pos'][2]} })

                    # --- [MỚI] Lưu file gameConfig vào base_maps để test ---
                    test_map_filename = f"{map_request.get('id', 'unknown')}-var{variant_index + 1}.json"
                    test_map_filepath = os.path.join(base_maps_output_dir, test_map_filename)
                    try:
                        with open(test_map_filepath, 'w', encoding='utf-8') as f:
                            json.dump(game_config, f, indent=2, ensure_ascii=False)
                        print(f"✅ Đã tạo thành công file map test: {test_map_filename}")
                    except Exception as e:
                        print(f"   - ⚠️ Lỗi khi lưu file map test: {e}")

                    # --- Bước 5: Lấy cấu hình Blockly ---
                    blockly_config_req = map_request.get('blockly_config', {})
                    toolbox_preset_name = blockly_config_req.get('toolbox_preset')
                    
                    # Lấy toolbox từ preset và tạo một bản sao để không làm thay đổi bản gốc
                    # (SỬA LỖI) Sử dụng deepcopy để tạo một bản sao hoàn toàn độc lập
                    base_toolbox = copy.deepcopy(toolbox_presets.get(toolbox_preset_name, {"kind": "categoryToolbox", "contents": []}))

                    # (CẢI TIẾN) Tự động thêm khối "Events" (when Run) vào đầu mỗi toolbox
                    events_category = {
                      "kind": "category",
                      "name": "%{BKY_GAMES_CATEVENTS}",
                      "categorystyle": "events_category",
                      "contents": [ { "kind": "block", "type": "maze_start" } ]
                    }
                    
                    # Đảm bảo 'contents' là một danh sách và chèn khối Events vào đầu
                    if 'contents' not in base_toolbox: base_toolbox['contents'] = []
                    base_toolbox['contents'].insert(0, events_category)
                    toolbox_data = base_toolbox
                    
                    # --- [CẢI TIẾN] Logic xử lý lời giải ---
                    solution_config = map_request.get('solution_config', {})
                    solution_config['logic_type'] = logic_type
                    
                    # [SỬA LỖI] Các logic_type này không thể giải bằng A* truyền thống.
                    # Chúng ta sẽ bỏ qua bước giải và tạo lời giải "giả lập" trực tiếp.
                    logic_types_to_skip_solving = [
                        'advanced_algorithm', 
                        'config_driven_execution',
                        'math_expression_loop',
                        'math_puzzle'
                    ]

                    solution_result = None
                    if logic_type not in logic_types_to_skip_solving:
                        # --- Bước 6: Gọi gameSolver để tìm lời giải (chỉ cho các map giải được bằng A*) ---
                        # [SỬA LỖI] Đảm bảo truyền đầy đủ thông tin, đặc biệt là gameConfig cho solver.
                        temp_level_for_solver = {
                            "gameConfig": game_config['gameConfig'],
                            "blocklyConfig": {"toolbox": toolbox_data},
                            "solution": solution_config
                        }
                        solution_result = solve_map_and_get_solution(temp_level_for_solver) # type: ignore
                    else:
                        print(f"    LOG: Bỏ qua bước giải A* cho logic_type '{logic_type}'. Sẽ tạo lời giải giả lập.")
                        # Tạo một đối tượng world để hàm synthesize_program có thể đọc
                        from scripts.gameSolver import GameWorld, synthesize_program, count_blocks, format_program_dict_for_json
                        world = GameWorld({
                            "gameConfig": game_config['gameConfig'], # type: ignore
                            "blocklyConfig": {"toolbox": toolbox_data},
                            "solution": solution_config
                        })
                        # Gọi trực tiếp hàm synthesize_program với một danh sách hành động trống
                        # vì lời giải sẽ được tạo dựa trên logic_type, không phải hành động.
                        program_dict = synthesize_program([], world)
                        solution_result = {
                            "block_count": count_blocks(program_dict),
                            "program_solution_dict": program_dict,
                            "raw_actions": [], # Không có hành động thô
                            "structuredSolution": program_dict
                        }

                    # [SỬA LỖI] Logic tính toán itemGoals và tạo map ánh xạ item_id -> type gốc
                    original_item_goals = map_request.get('solution_config', {}).get('itemGoals', {})
                    final_item_goals = {}
                    item_id_to_type_map = {}

                    # Đếm số lượng yêu cầu cho mỗi loại item từ curriculum
                    from collections import Counter
                    required_item_counts = Counter(params_for_generation.get('items_to_place', []))

                    # Tạo map ánh xạ và tính toán final_item_goals
                    for item_obj in generated_map.items:
                        item_id = item_obj.get('id')
                        item_type = item_obj.get('type') # Đây là type gốc (crystal, gem, key)
                        if item_id and item_type:
                            item_id_to_type_map[item_id] = item_type

                    # Cập nhật final_item_goals dựa trên số lượng yêu cầu
                    for item_type, count in required_item_counts.items():
                        final_item_goals[item_type] = count
                        print(f"    LOG: Đã tính toán itemGoals cho '{item_type}': {count}")


                    # --- [MỚI] Bước 6.5: Tính toán Optimal Lines of Code cho JavaScript ---
                    optimal_lloc = 0
                    if solution_result and solution_result.get('structuredSolution'):
                        # [CẢI TIẾN] Tính toán LLOC trực tiếp từ structuredSolution
                        optimal_lloc = calculate_optimal_lines_from_structured(solution_result.get('program_solution_dict', {}))

                    # --- Logic mới để sinh startBlocks động cho các thử thách FixBug ---
                    final_inner_blocks = ''
                    # [MỚI] Khởi tạo các biến cho phiên bản lỗi
                    buggy_program_dict = None
                    structured_solution_fixbug = None

                    start_blocks_type = generation_config.get("params", {}).get("start_blocks_type", "empty")

                    # [CẢI TIẾN LỚN] Logic sinh startBlocks
                    program_dict = solution_result.get("program_solution_dict", {}) if solution_result else {}
                    if start_blocks_type == "buggy_solution" and solution_result:
                        print("    LOG: Bắt đầu quy trình tạo lỗi cho 'buggy_solution'.")
                        bug_type = generation_config.get("params", {}).get("bug_type")
                        bug_config = generation_config.get("params", {}).get("bug_config", {}) or {}

                        # [REWRITTEN] Logic tạo lỗi theo kiến trúc mới
                        # Bước 1: Tạo bản sao của lời giải đúng để chỉnh sửa
                        original_program_dict = solution_result.get("program_solution_dict", {})
                        program_to_be_bugged = copy.deepcopy(original_program_dict)

                        # Bước 2: Gọi service để tạo lỗi trực tiếp trên dictionary
                        # Giả định `create_bug` giờ đây nhận và trả về dict
                        # Nếu bug_type là 'optimization_logic', startBlocks là lời giải chưa tối ưu
                        if bug_type in {'optimization_logic', 'optimization_no_variable'}:
                            print(f"    LOG: Tạo bug tối ưu hóa, sử dụng lời giải thô làm startBlocks.")
                            raw_actions = solution_result.get("raw_actions", [])
                            inner_xml = actions_to_xml(raw_actions)
                            final_inner_blocks = f'<block type="maze_start" deletable="false" movable="false"><statement name="DO">{inner_xml}</statement></block>' # noqa
                            # Trong trường hợp này, không có structuredSolution_fixbug_version
                        else:
                            buggy_program_dict = create_bug(bug_type, program_to_be_bugged, bug_config)

                            # Bước 3: Từ `buggy_program_dict`, tạo ra các output cần thiết
                            # [FIX] Kiểm tra xem create_bug có trả về dict hợp lệ không.
                            # Một số hàm bug cũ có thể trả về string (XML) khi thất bại.
                            if isinstance(buggy_program_dict, dict):
                                # [FIX] Tạo XML cho startBlocks.
                                # Đối với lỗi incorrect_block, raw_actions của lời giải gốc vẫn có thể
                                # được dùng để xác định hướng rẽ cho các khối 'turn' không bị thay đổi.
                                raw_actions_for_bug = solution_result.get("raw_actions", []) if bug_type in ['incorrect_block', 'incorrect_parameter'] else None
                                final_inner_blocks = _create_xml_from_structured_solution(buggy_program_dict, raw_actions_for_bug)
                                # Tạo phiên bản text của lời giải lỗi
                                structured_solution_fixbug = buggy_program_dict
                                print("    LOG: Đã tạo thành công phiên bản lỗi của lời giải.")
                            else:
                                # [SỬA LỖI] Xử lý khi create_bug không trả về dict
                                # Nếu create_bug trả về string hoặc None, nghĩa là đã có lỗi xảy ra.
                                # In cảnh báo và sử dụng lại XML của lời giải đúng để không làm gián đoạn.
                                print(f"   - ⚠️ Cảnh báo: Hàm tạo lỗi cho bug_type '{bug_type}' không trả về dictionary. Có thể lỗi đã không được tạo.")
                                print(f"   - INFO: Sử dụng lời giải đúng làm startBlocks để tiếp tục.")
                                final_inner_blocks = _create_xml_from_structured_solution(original_program_dict)
                                # Không tạo structured_solution_fixbug trong trường hợp này.
                                print(f"   - ⚠️ Cảnh báo: Không thể tạo lỗi cho bug_type '{bug_type}'.")
                                final_inner_blocks = '' # Để trống nếu không tạo được lỗi
                    
                    elif start_blocks_type in ["raw_solution", "unrefactored_solution"] and solution_result:
                        # Cung cấp lời giải tuần tự (chưa tối ưu)
                        raw_actions = solution_result.get("raw_actions", [])
                        # [SỬA LỖI] Bọc các khối tuần tự trong một khối maze_start
                        inner_xml = actions_to_xml(raw_actions)
                        final_inner_blocks = f'<block type="maze_start" deletable="false" movable="false"><statement name="DO">{inner_xml}</statement></block>'
                    
                    elif start_blocks_type == "optimized_solution" and solution_result:
                        # Cung cấp lời giải đã tối ưu
                        final_inner_blocks = _create_xml_from_structured_solution(program_dict, solution_result.get("raw_actions", []))
                    elif 'start_blocks' in blockly_config_req and blockly_config_req['start_blocks']:
                        raw_start_blocks = blockly_config_req['start_blocks']
                        # [CẢI TIẾN] Sử dụng XML parser để trích xuất nội dung một cách an toàn
                        try:
                            root = ET.fromstring(raw_start_blocks)
                            final_inner_blocks = "".join(ET.tostring(child, encoding='unicode') for child in root)
                        except ET.ParseError:
                            print(f"   - ⚠️ Cảnh báo: Lỗi cú pháp XML trong 'start_blocks' được định nghĩa sẵn. Sử dụng chuỗi thô.")
                            final_inner_blocks = raw_start_blocks.replace('<xml>', '').replace('</xml>', '')
                    
                    if final_inner_blocks:
                        # [SỬA LỖI] Đảm bảo thẻ <xml> luôn được thêm vào, ngay cả khi final_inner_blocks đã chứa nó
                        if not final_inner_blocks.strip().startswith('<xml>'):
                             final_start_blocks = f"<xml>{final_inner_blocks}</xml>"
                        else:
                             final_start_blocks = final_inner_blocks # Đã có thẻ <xml>
                    else:
                        # Mặc định: tạo một khối maze_start rỗng
                        final_start_blocks = "<xml><block type=\"maze_start\" deletable=\"false\" movable=\"false\"><statement name=\"DO\"></statement></block></xml>"

                    # [CẢI TIẾN] Chuẩn bị dữ liệu translations và topic key duy nhất
                    topic_key = f"topic-title-{topic_code.lower()}"
                    topic_name_en = TOPIC_TRANSLATIONS.get(topic_name_vi, topic_name_vi) # Lấy bản dịch, nếu không có thì dùng tên gốc
                    final_translations = copy.deepcopy(map_request.get('translations', {}))
                    # Thêm bản dịch cho topic title
                    if 'vi' in final_translations:
                        final_translations['vi'][topic_key] = topic_name_vi
                    if 'en' in final_translations:
                        final_translations['en'][topic_key] = topic_name_en

                    # --- Bước 7: Tổng hợp file JSON cuối cùng ---
                    final_json = {
                        "id": f"{map_request.get('id', 'unknown')}-var{variant_index + 1}",
                        "gameType": "maze",
                        "grade": 4,
                        "topic": topic_key, # [SỬA] Sử dụng topic key duy nhất
                        "level": map_request.get('level', 1),
                        "titleKey": map_request.get('titleKey'),
                        "questTitleKey": map_request.get('descriptionKey'),
                        "descriptionKey": map_request.get('descriptionKey'), # [MỚI] Thêm trường topic
                        "translations": final_translations, # [MỚI] Sử dụng translations đã bổ sung
                        "supportedEditors": ["blockly", "monaco"],
                        "blocklyConfig": {
                            "toolbox": toolbox_data,
                            "maxBlocks": (solution_result['block_count'] + 5) if solution_result else 99,
                            "startBlocks": final_start_blocks
                        },
                        "gameConfig": game_config['gameConfig'],
                        "solution": {
                            #"type": map_request.get('solution_config', {}).get('type', 'reach_target'),
                            "type": "reach_target",
                            "itemGoals": final_item_goals,
                            "optimalBlocks": solution_result['block_count'] if solution_result else 0,
                            "optimalLines": optimal_lloc, # Lời giải đúng
                            "rawActions": solution_result['raw_actions'] if solution_result else [],
                            "structuredSolution": solution_result.get('program_solution_dict', {}) if solution_result else {}, # Lời giải đúng
                            "item_id_to_type_map": item_id_to_type_map # [SỬA LỖI] Thêm map ánh xạ
                        },
                        "sounds": { "win": "/assets/maze/win.mp3", "fail": "/assets/maze/fail_pegman.mp3" }
                    }

                    # [MỚI] Thêm trường structuredSolution_fixbug_version nếu có
                    if structured_solution_fixbug:
                        final_json["solution"]["structuredSolution_fixbug_version"] = structured_solution_fixbug

                    # --- Bước 8: Lưu file JSON cuối cùng ---
                    filename = f"{final_json['id']}.json"
                    output_filepath = os.path.join(final_output_dir, filename)
                    with open(output_filepath, 'w', encoding='utf-8') as f:
                        json.dump(final_json, f, indent=2, ensure_ascii=False)                
                    print(f"✅ Đã tạo thành công file game hoàn chỉnh: {filename}")
                    total_maps_generated += 1
                    
                except Exception as e:
                    print(f"   ❌ Lỗi khi sinh biến thể {variant_index + 1} cho yêu cầu #{request_index + 1}: {e}")
                    total_maps_failed += 1
                    # Nếu một biến thể bị lỗi, bỏ qua các biến thể còn lại của map request này
                    break 

    # --- Bước 6: In báo cáo tổng kết ---
    print("\n=============================================")
    print("=== KẾT THÚC QUY TRÌNH SINH MAP ===")
    print(f"📊 Báo cáo: Đã tạo thành công {total_maps_generated} file game, thất bại {total_maps_failed} file.")
    print(f"📂 Các file game đã được lưu tại: {final_output_dir}")
    print(f"📂 Các file map test đã được lưu tại: {base_maps_output_dir}")
    print("=============================================")

if __name__ == "__main__":
    # Điểm khởi chạy của script
    main()