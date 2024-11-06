# Copyright © 2024 [李博远，何悦]
# The MIT License (MIT)
# 本代码通过MIT许可。允许任何人自由使用、修改、分发代码。
# 不可以用于作弊目的，仅用于学习研究。

import cv2
import numpy as np
import pyautogui
import time
import subprocess
import os

# 终于做好咯。
# 未来的几个方向：
# 1，不断增加数据集。但是需要考虑时间，因为每次都会遍历全部数据集，涉及大量的计算。
# 2，此代码基础上，每次跳之前都增加一个数据点。（和1类似，执行起来难度稍高，需要大规模修改代码）
# 3，一个完全新的思路，摒弃了计算机视觉（算力需求），直接每次选取起终点，输入到程序中，自动计算距离和按压时间。

time.sleep(3)

# 1. 截取屏幕图像并保存到 'pic' 文件夹
def capture_screen():
    screenshot = pyautogui.screenshot()
    screenshot = np.array(screenshot)
    screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)
    
    if not os.path.exists('pic'):
        os.makedirs('pic')

    screenshot_path = os.path.join('pic', f"screenshot_{int(time.time())}.png")
    cv2.imwrite(screenshot_path, screenshot)
    print(f"Screenshot saved to {screenshot_path}")
    
    return screenshot

# 2. 识别玩家和目标位置
def detect_positions(image):
    channels = cv2.split(image)
    
    # 动态加载玩家和目标模板
    player_templates = load_templates('player')
    target_templates = load_templates('target')
    
    # 初始化玩家和目标位置和最大信心度
    player_pos, target_pos = None, None
    max_player_confidence, max_target_confidence = 0, 0

    # 检查模板尺寸
    def check_template_size(image, template):
        if template.shape[0] > image.shape[0] or template.shape[1] > image.shape[1]:
            print("Template is larger than image. Skipping this template.")
            return False
        return True
    
    #########################################
    ###############玩家模板匹配###############
    #########################################
    for player_template in player_templates:
        if player_template is None or not check_template_size(image, player_template):
            continue

        template_channels = cv2.split(player_template)
        max_val_sum, max_loc_sum = 0, (0, 0)

        # 在每个通道上进行模板匹配并平均结果
        for ch, template_ch in zip(channels, template_channels):
            res = cv2.matchTemplate(ch, template_ch, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(res)
            max_val_sum += max_val
            max_loc_sum = tuple(map(sum, zip(max_loc_sum, max_loc)))
        
        avg_max_val = max_val_sum / 3
        avg_max_loc = tuple([int(x / 3) for x in max_loc_sum])

        if avg_max_val > max_player_confidence:
            max_player_confidence = avg_max_val
            player_pos = avg_max_loc
            player_size = player_template.shape[1], player_template.shape[0]  # width, height

    #########################################
    ###############目标模板匹配###############
    #########################################
    for target_template in target_templates:
        if target_template is None or not check_template_size(image, target_template):
            continue

        template_channels = cv2.split(target_template)
        max_val_sum, max_loc_sum = 0, (0, 0)

        # 在每个通道上进行模板匹配并平均结果
        for ch, template_ch in zip(channels, template_channels):
            res = cv2.matchTemplate(ch, template_ch, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(res)
            max_val_sum += max_val
            max_loc_sum = tuple(map(sum, zip(max_loc_sum, max_loc)))

        avg_max_val = max_val_sum / 3
        avg_max_loc = tuple([int(x / 3) for x in max_loc_sum])

        # 确保目标在玩家上方
        if player_pos and avg_max_loc[1] >= player_pos[1]:
            print(f"Skipping target below player at position {avg_max_loc}")
            continue

        if avg_max_val > max_target_confidence:
            max_target_confidence = avg_max_val
            target_pos = avg_max_loc
            target_size = target_template.shape[1], target_template.shape[0]  # width, height

    print(f"Max player confidence: {max_player_confidence}")
    print(f"Max target confidence: {max_target_confidence}")

    if max_player_confidence < 0.01 or max_target_confidence < 0.01:  
        print("Error: Low confidence detected. Returning None.")
        return None, None  
    
    # Calculate dynamic bounding box for player and target based on their detected sizes
    def get_center_position(pos, width, height):
        return (pos[0] + width // 2, pos[1] + height // 2)
    
    if player_pos:
        player_pos = get_center_position(player_pos, *player_size)  # Use dynamic player size
    if target_pos:
        target_pos = get_center_position(target_pos, *target_size)  # Use dynamic target size

    return player_pos, target_pos


# 3. 计算玩家和目标之间的距离
def calculate_distance(player_pos, target_pos):
    return np.sqrt((target_pos[0] - player_pos[0]) ** 2 + (target_pos[1] - player_pos[1]) ** 2)

# 4. 根据距离模拟点击跳跃
def press_for_jump(distance):
    press_time = int(distance * 2.55)  
    x1, y1 = 500, 500  
    subprocess.run(["D:\\jump_game\\scrcpy-win64-v2.7\\adb.exe", "shell", "input", "swipe", str(x1), str(y1), str(x1), str(y1), str(press_time)])
    print(f"Jumping with press time: {press_time} ms (based on distance: {distance})")

# 5. 通过 ADB 执行操作（可选，适用于安卓手机）
def adb_swipe(x1, y1, x2, y2, duration):
    subprocess.run(["D:\\jump_game\\scrcpy-win64-v2.7\\adb.exe", "shell", "input", "swipe", str(x1), str(y1), str(x2), str(y2), str(duration)])

# 6. 可视化玩家和目标位置
def visualize_jump(image, player_pos, target_pos, player_size, target_size):
    if player_pos is not None:
        player_rect_start = (player_pos[0] - player_size[0] // 2, player_pos[1] - player_size[1] // 2)
        player_rect_end = (player_pos[0] + player_size[0] // 2, player_pos[1] + player_size[1] // 2)
        cv2.rectangle(image, player_rect_start, player_rect_end, (0, 0, 255), 2)  # Red rectangle
    
    if target_pos is not None:
        target_rect_start = (target_pos[0] - target_size[0] // 2, target_pos[1] - target_size[1] // 2)
        target_rect_end = (target_pos[0] + target_size[0] // 2, target_pos[1] + target_size[1] // 2)
        cv2.rectangle(image, target_rect_start, target_rect_end, (0, 255, 0), 2)  # Green rectangle

    if not os.path.exists('piccc'):
        os.makedirs('piccc')

    visualized_path = os.path.join('piccc', f"visualized_{int(time.time())}.png")
    cv2.imwrite(visualized_path, image)
    print(f"Visualized image saved to {visualized_path}")

# 7. 加载模板图片
def load_templates(folder_name):
    templates = []
    folder_path = os.path.join(os.getcwd(), folder_name)
    if os.path.exists(folder_path):
        for filename in os.listdir(folder_path):
            if filename.endswith('.png'):
                template = cv2.imread(os.path.join(folder_path, filename))
                if template is not None:
                    templates.append(template)
    return templates

# 主程序
def main():
    while True:
        screenshot = capture_screen()

        player_pos, target_pos = detect_positions(screenshot)

        if player_pos == (0, 0) or target_pos == (0, 0):
            print("Error: Could not detect player or target. Retrying...")
            continue

        # Get the actual sizes of the detected player and target templates for visualization
        player_size = (47, 134)  # Default size for visualization purposes
        target_size = (197, 165)  # Default size for visualization purposes
        visualize_jump(screenshot, player_pos, target_pos, player_size, target_size)

        distance = calculate_distance(player_pos, target_pos)
        press_for_jump(distance)

        # Slight delay to avoid rapid repetitive jumps
        time.sleep(3)

if __name__ == "__main__":
    main()
