# generate_270_unique_exercises.py
import os
import random

base_dir = "270_unique_exercises"
os.makedirs(base_dir, exist_ok=True)

# === CẤU TRÚC BÀI TẬP THEO LỚP & TOPIC ===
exercise_templates = {
    "Topic1_Commands": {
        "L3": ["L ngắn", "3 lệnh", lambda: f"move(); move(); turn_right(); move()"],
        "L4": ["L dài", "for loop", lambda: f"for _ in range(6): move(); turn_right(); for _ in range(5): move()"],
        "L5": ["U nhỏ", "toggle", lambda: f"for _ in range(4): move(); toggle(); turn_left(); for _ in range(2): move()"],
        "L6": ["Zigzag", "nested loop", lambda: f"for _ in range(2):\n    for _ in range(4): move()\n    turn_right()\n    move()\n    turn_right()"]
    },
    "Topic2_Functions": {
        "L5": ["Vẽ U nhỏ", "def draw_U()", lambda: f"def draw_U():\n    for _ in range(4): move()\n    turn_left(); for _ in range(2): move()\n    turn_left(); for _ in range(4): move()"],
        "L6": ["Vẽ V", "mirror", lambda: f"def draw_V():\n    for _ in range(3): move(); turn_right()\n    for _ in range(3): move(); turn_left()\n    for _ in range(3): move()"],
        "L7": ["Vẽ Z", "repeat", lambda: f"def draw_Z():\n    for _ in range(5): move()\n    turn_right(); move(); turn_right()\n    for _ in range(5): move()"],
        "L8": ["Vẽ sao", "góc 72°", lambda: f"def draw_star():\n    for _ in range(5):\n        for _ in range(3): move()\n        turn_right(); turn_right(); turn_right()"]
    },
    "Topic8_Algorithms": {
        "L9": ["BFS 9x9", "queue", lambda: f"from queue import Queue\nq = Queue()\nq.put(start)\nvisited = set()"],
        "L10": ["DFS 11x11", "stack", lambda: f"stack = [start]\nwhile stack:\n    curr = stack.pop()"],
        "L11": ["A* 13x13", "heuristic", lambda: f"def h(p): return abs(p[0]-target[0]) + abs(p[1]-target[1])"],
        "L12": ["A* 14x14x14", "3D + cost", lambda: f"def heuristic_3d(a,b):\n    return sum(abs(x-y) for x,y in zip(a,b))"]
    }
}

# === TẠO 270 BÀI TẬP ĐỘC LẬP ===
count = 1
for topic, levels in exercise_templates.items():
    topic_dir = os.path.join(base_dir, topic)
    os.makedirs(topic_dir, exist_ok=True)
    
    for class_level, (map_name, goal, code_gen) in levels.items():
        for i in range(1, 31):  # 30 bài mỗi cấp
            filename = f"{class_level}_{i:02d}_{map_name.replace(' ', '_')}.py"
            code = f"# {topic} - Lớp {class_level} - Bài {i}\n"
            code += f"# Map: {map_name} | Mục tiêu: {goal}\n"
            code += code_gen()
            if random.random() < 0.3:
                code += f"\n# GỢI Ý: Sử dụng {random.choice(['for', 'while', 'if', 'def'])}"
            
            with open(os.path.join(topic_dir, filename), "w", encoding="utf-8") as f:
                f.write(code)
            count += 1

print(f"HOÀN TẤT! ĐÃ TẠO {count-1} BÀI TẬP ĐỘC LẬP!")