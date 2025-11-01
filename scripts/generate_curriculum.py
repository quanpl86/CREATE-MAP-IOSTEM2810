# scripts/generate_curriculum.py
import pandas as pd
import json
import os
import re
from collections import defaultdict

# --- Cấu hình đường dẫn ---
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Thay đổi tên file nguồn nếu bạn sử dụng tên khác, ví dụ: 'master_curriculum_source.xlsx'
INPUT_FILE = os.path.join(PROJECT_ROOT, 'data', 'curriculum_source.xlsx')
OUTPUT_DIR = os.path.join(PROJECT_ROOT, 'data', 'curriculum')


# --- [NÂNG CẤP] Hàm parse_params được cải tiến để xử lý JSON objects và arrays ---
def parse_params(param_string):
    """
    Chuyển đổi chuỗi 'key1:value1;key2:{"k":"v"};key3:[1,2]' thành dictionary.
    Hỗ trợ các giá trị dạng: chuỗi, số nguyên, JSON object, và JSON array.
    """
    if not isinstance(param_string, str) or not param_string.strip():
        return {}
    params = {}
    # Phân tách các cặp key-value bằng dấu chấm phẩy
    for part in param_string.split(';'):
        if ':' in part:
            key, value = part.split(':', 1)
            key = key.strip()
            value = value.strip()
            
            # Cố gắng chuyển đổi value thành kiểu dữ liệu phù hợp
            try:
                # 1. Kiểm tra xem value có phải là một JSON object hoặc array không
                if (value.startswith('{') and value.endswith('}')) or \
                   (value.startswith('[') and value.endswith(']')):
                    # Thay thế nháy đơn bằng nháy kép để đảm bảo JSON hợp lệ
                    valid_json_string = value.replace("'", '"')
                    params[key] = json.loads(valid_json_string)
                # 2. Nếu không, thử chuyển đổi thành số nguyên
                else:
                    params[key] = int(value)
            except (ValueError, json.JSONDecodeError):
                # 3. Nếu tất cả thất bại, giữ nguyên giá trị là chuỗi
                params[key] = value
    return params


def main():
    """Đọc file Excel và sinh ra các file curriculum JSON."""
    print("=============================================")
    print("=== BẮT ĐẦU QUY TRÌNH SINH CURRICULUM ===")
    print("=============================================")

    try:
        # Sử dụng .fillna('') để xử lý các ô trống, tránh lỗi
        df = pd.read_excel(INPUT_FILE).fillna('')
        print(f"✅ Đọc thành công file nguồn: {INPUT_FILE}")
    except FileNotFoundError:
        print(f"❌ Lỗi: Không tìm thấy file nguồn '{INPUT_FILE}'.")
        return
    except Exception as e:
        print(f"❌ Lỗi khi đọc file Excel: {e}")
        return

    # Nhóm các thử thách theo topic_code
    challenges_by_topic = defaultdict(lambda: {'topic_name': '', 'suggested_maps': []})

    # Lặp qua từng dòng trong file Excel để tạo cấu trúc map
    for index, row in df.iterrows():
        topic_code = row['topic_code']
        challenges_by_topic[topic_code]['topic_name'] = row['topic_name']

        # Tạo cấu trúc cho một map_request
        map_request = {
            "id": row['id'],
            "level": int(row['level']),
            "titleKey": f"Challenge.{row['id']}.Title",
            "descriptionKey": f"Challenge.{row['id']}.Description",
            "translations": {}, # Khởi tạo translations rỗng để điền sau
            "generation_config": {
                "map_type": row['gen_map_type'],
                "logic_type": row['gen_logic_type'],
                # [CẢI TIẾN] Cung cấp giá trị mặc định là 1 nếu ô trống
                "num_variants": int(row.get('gen_num_variants')) if row.get('gen_num_variants') else 1,
                "params": parse_params(row.get('gen_params', '')) # Sử dụng hàm parse_params đã nâng cấp
            },
            "blockly_config": {
                "toolbox_preset": row['blockly_toolbox_preset'],
            },
            "solution_config": {
                # [CẢI TIẾN] Cung cấp giá trị mặc định nếu cột không tồn tại
                "type": row.get('solution_type', 'reach_target'),
                "itemGoals": parse_params(row.get('solution_item_goals', ''))
            }
        }
        
        # --- [NÂNG CẤP] Tự động điền các bản dịch từ file Excel ---
        # Điền bản dịch Tiếng Việt
        if 'title_vi' in df.columns and row['title_vi']:
            map_request['translations']['vi'] = {
                f"Challenge.{row['id']}.Title": row['title_vi'],
                f"Challenge.{row['id']}.Description": row['description_vi']
            }
        
        # Điền bản dịch Tiếng Anh nếu có
        if 'title_en' in df.columns and row['title_en']:
            map_request['translations']['en'] = {
                f"Challenge.{row['id']}.Title": row['title_en'],
                f"Challenge.{row['id']}.Description": row['description_en']
            }

        # [CẢI TIẾN] Chỉ thêm các khối blockly khởi đầu nếu chúng thực sự được định nghĩa
        if row.get('blockly_start_block_type'):
             map_request["blockly_config"]["start_block_type"] = row.get('blockly_start_block_type')
        if row.get('blockly_start_blocks'):
             map_request["blockly_config"]["start_blocks"] = row.get('blockly_start_blocks')

        challenges_by_topic[topic_code]['suggested_maps'].append(map_request)

    # Ghi ra các file JSON cho từng topic
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"📁 Đã tạo thư mục output: {OUTPUT_DIR}")

    for topic_code, data in challenges_by_topic.items():
        # [CẢI TIẾN] Sắp xếp các map theo level trước khi ghi file
        data['suggested_maps'].sort(key=lambda x: x['level'])
        
        # [CẢI TIẾN] Tạo tên file thân thiện và an toàn hơn
        match = re.search(r'TOPIC_(\d+)', topic_code)
        if match:
            topic_num = match.group(1)
            # Chuẩn hóa topic_name để làm tên file, loại bỏ ký tự không an toàn
            safe_topic_name = data['topic_name'].lower()
            safe_topic_name = re.sub(r'[\s&]+', '_', safe_topic_name) # Thay khoảng trắng, & bằng _
            safe_topic_name = re.sub(r'[^\w-]', '', safe_topic_name) # Loại bỏ các ký tự không phải chữ, số, _, -
            filename = f"{topic_num}_{safe_topic_name}.json"
        else:
            filename = f"{topic_code.lower()}.json"

        output_path = os.path.join(OUTPUT_DIR, filename)
        
        final_json = {
            "topic_code": topic_code,
            "topic_name": data['topic_name'],
            "suggested_maps": data['suggested_maps']
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            # indent=2 để file JSON dễ đọc, ensure_ascii=False để hiển thị tiếng Việt
            json.dump(final_json, f, indent=2, ensure_ascii=False)
        print(f"✅ Đã tạo/cập nhật file curriculum: {filename}")

    print("\n=============================================")
    print("=== HOÀN THÀNH SINH CURRICULUM ===")
    print("=============================================")


if __name__ == "__main__":
    main()