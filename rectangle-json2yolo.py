import json
import os


def convert_json_to_yolo(json_file):
    try:
        # 读取JSON文件
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 获取图片尺寸
        img_width = data['imageWidth']
        img_height = data['imageHeight']

        # 获取JSON文件所在的目录
        json_dir = os.path.dirname(json_file)

        # 创建输出文件名
        base_name = os.path.splitext(os.path.basename(json_file))[0]
        output_file = os.path.join(json_dir, f"{base_name}.txt")

        # 确保输出目录存在
        output_dir = os.path.dirname(output_file)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # 标签映射字典
        label_map = {
            'aphid': 0
        }

        # 开始转换
        yolo_lines = []

        # 检查shapes是否为空
        if not data['shapes']:
            print(f"警告: {json_file} 没有标注数据")
            # 仍然创建空文件
            with open(output_file, 'w') as f:
                f.write('')
            return False

        for shape in data['shapes']:
            # 获取标签
            label = shape['label']
            if label not in label_map:
                print(f"警告: 文件 {json_file} 中存在未知标签 {label}")
                continue

            # 获取边界框坐标
            points = shape['points']
            x1, y1 = points[0]
            x2, y2 = points[2]

            # 计算YOLO格式的中心点坐标和宽高
            x_center = (x1 + x2) / (2 * img_width)
            y_center = (y1 + y2) / (2 * img_height)
            width = abs(x2 - x1) / img_width
            height = abs(y2 - y1) / img_height

            # 确保值在0-1范围内
            x_center = min(max(x_center, 0), 1)
            y_center = min(max(y_center, 0), 1)
            width = min(max(width, 0), 1)
            height = min(max(height, 0), 1)

            # 格式化YOLO行
            yolo_line = f"{label_map[label]} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}"
            yolo_lines.append(yolo_line)

        # 写入输出文件
        with open(output_file, 'w') as f:
            f.write('\n'.join(yolo_lines))

        return True

    except Exception as e:
        print(f"处理文件 {json_file} 时出错: {str(e)}")
        return False


# 使用示例
if __name__ == "__main__":
    json_dir = r"F:\\apycharm1\\video_caption\ed\\aphid_output_auto"  # 修改为你的JSON文件目录

    # 统计信息
    total_files = 0
    successful_conversions = 0
    failed_files = []
    empty_files = []

    # 处理所有JSON文件
    for filename in os.listdir(json_dir):
        if filename.endswith('.json'):
            total_files += 1
            json_file = os.path.join(json_dir, filename)

            if convert_json_to_yolo(json_file):
                successful_conversions += 1
            else:
                failed_files.append(filename)

            # 检查JSON文件是否为空
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if not data['shapes']:
                    empty_files.append(filename)

    # 打印统计信息
    print("\n转换统计:")
    print(f"总文件数: {total_files}")
    print(f"成功转换: {successful_conversions}")
    print(f"失败文件数: {len(failed_files)}")
    print(f"空标注文件数: {len(empty_files)}")

    if failed_files:
        print("\n失败的文件:")
        for file in failed_files:
            print(file)

    if empty_files:
        print("\n空标注的文件:")
        for file in empty_files:
            print(file)
# 使用示例
