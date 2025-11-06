#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import shutil
import xml.etree.ElementTree as ET
from PIL import Image
import xml.dom.minidom

# --- 参数设定 ---
# YOLO 数据集的根目录（其中包含 images/ 与 labels/ 文件夹）
yolo_dir = r"/faster-rcnn-pytorch/lakuang"

# 输出的 VOC 格式数据集目录
voc_dir = r"/faster-rcnn-pytorch/lakuang-voc"

# YOLO 数据集类别（请按照你的数据集类别顺序填写）
classes = ["yachong"]

# 数据集划分，不需要重新划分，因此直接按照已有的 train、val、test 子文件夹进行处理
splits = ["train", "val", "test"]

# --- 创建 VOC 数据集目录结构 ---
os.makedirs(os.path.join(voc_dir, "Annotations"), exist_ok=True)
os.makedirs(os.path.join(voc_dir, "JPEGImages"), exist_ok=True)
os.makedirs(os.path.join(voc_dir, "ImageSets", "Main"), exist_ok=True)

# 用于保存各划分内的图片 id（不包含扩展名）
split_ids = {s: [] for s in splits}

# --- 遍历每个划分，转换标签并复制图片 ---
for split in splits:
    image_folder = os.path.join(yolo_dir, "images", split)
    label_folder = os.path.join(yolo_dir, "labels", split)

    # 支持的图片扩展名
    image_extensions = ['.jpg', '.jpeg', '.png']
    image_files = [f for f in os.listdir(image_folder)
                   if os.path.splitext(f)[1].lower() in image_extensions]

    for img_file in image_files:
        img_path = os.path.join(image_folder, img_file)
        # 取得图片 id（文件名不带扩展名）
        img_id = os.path.splitext(img_file)[0]
        split_ids[split].append(img_id)

        # 打开图片，获取尺寸
        im = Image.open(img_path)
        width, height = im.size
        # 根据图片通道判断深度
        if im.mode == "RGB":
            depth = 3
        elif im.mode == "L":
            depth = 1
        else:
            depth = 3

        # --- 构造 VOC 格式 XML ---
        annotation = ET.Element("annotation")

        folder_el = ET.SubElement(annotation, "folder")
        folder_el.text = os.path.basename(voc_dir)

        filename_el = ET.SubElement(annotation, "filename")
        filename_el.text = img_file

        source = ET.SubElement(annotation, "source")
        database = ET.SubElement(source, "database")
        database.text = "Unknown"

        size_el = ET.SubElement(annotation, "size")
        width_el = ET.SubElement(size_el, "width")
        width_el.text = str(width)
        height_el = ET.SubElement(size_el, "height")
        height_el.text = str(height)
        depth_el = ET.SubElement(size_el, "depth")
        depth_el.text = str(depth)

        segmented = ET.SubElement(annotation, "segmented")
        segmented.text = "0"

        # 查找对应的标签文件（YOLO 的 .txt 文件）
        label_path = os.path.join(label_folder, img_id + ".txt")
        if os.path.exists(label_path):
            with open(label_path, "r") as f:
                lines = f.readlines()
                for line in lines:
                    line = line.strip()
                    if line == "":
                        continue
                    parts = line.split()
                    if len(parts) != 5:
                        continue
                    class_id, x_center, y_center, bbox_width, bbox_height = parts
                    class_id = int(class_id)
                    x_center = float(x_center)
                    y_center = float(y_center)
                    bbox_width = float(bbox_width)
                    bbox_height = float(bbox_height)

                    # 将 YOLO 的归一化坐标转换为像素坐标
                    x_center_abs = x_center * width
                    y_center_abs = y_center * height
                    bbox_width_abs = bbox_width * width
                    bbox_height_abs = bbox_height * height

                    xmin = int(x_center_abs - bbox_width_abs / 2)
                    ymin = int(y_center_abs - bbox_height_abs / 2)
                    xmax = int(x_center_abs + bbox_width_abs / 2)
                    ymax = int(y_center_abs + bbox_height_abs / 2)

                    # 保证边界在图片内
                    xmin = max(0, xmin)
                    ymin = max(0, ymin)
                    xmax = min(width, xmax)
                    ymax = min(height, ymax)

                    obj = ET.SubElement(annotation, "object")
                    name = ET.SubElement(obj, "name")
                    # 防止类别 id 超出定义范围
                    name.text = classes[class_id] if class_id < len(classes) else str(class_id)
                    pose = ET.SubElement(obj, "pose")
                    pose.text = "Unspecified"
                    truncated = ET.SubElement(obj, "truncated")
                    truncated.text = "0"
                    difficult = ET.SubElement(obj, "difficult")
                    difficult.text = "0"

                    bndbox = ET.SubElement(obj, "bndbox")
                    xmin_el = ET.SubElement(bndbox, "xmin")
                    xmin_el.text = str(xmin)
                    ymin_el = ET.SubElement(bndbox, "ymin")
                    ymin_el.text = str(ymin)
                    xmax_el = ET.SubElement(bndbox, "xmax")
                    xmax_el.text = str(xmax)
                    ymax_el = ET.SubElement(bndbox, "ymax")
                    ymax_el.text = str(ymax)

        # --- 保存 XML 文件 ---
        # 生成整齐的 XML 字符串（可选格式化）
        xml_str = ET.tostring(annotation, encoding="utf-8")
        dom = xml.dom.minidom.parseString(xml_str)
        pretty_xml = dom.toprettyxml(indent="    ")

        xml_output_path = os.path.join(voc_dir, "Annotations", img_id + ".xml")
        with open(xml_output_path, "w", encoding="utf-8") as xml_file:
            xml_file.write(pretty_xml)

        # --- 复制图片至 VOC dataset 的 JPEGImages 文件夹 ---
        shutil.copy(img_path, os.path.join(voc_dir, "JPEGImages", img_file))

# --- 根据划分生成 ImageSets/Main 下的 train.txt、val.txt、test.txt ---
for split in splits:
    split_file = os.path.join(voc_dir, "ImageSets", "Main", split + ".txt")
    with open(split_file, "w", encoding="utf-8") as f:
        for img_id in split_ids[split]:
            f.write(img_id + "\n")

print("转换完成！")