# Ebike Warning Tone Experiment – Data Plot & Map Generator  

## Overview | 项目简介

**English**  
This repository contains a Python script that reads one or multiple CSV files produced in the *E-bike Warning Tone Experiment*,  
plots the speed-versus-time curves (highlighting over-speed segments) and, if you provide an AMap (高德地图) API key, generates interactive HTML maps showing the riding path and the overspeeding points.

**中文**  
本仓库提供一段 Python 脚本，可读取 *电动车警示音实验* 产生的一个或多个 CSV 数据表，  
绘制速度-时间曲线（超速部分自动高亮），并可在输入高德地图 API Key 的情况下，输出带骑行轨迹与超速点的交互式 HTML 地图。

## Directory Structure | 目录结构
```text
.
├── csv/                # ↳ put all CSV data files here / 放置所有 CSV 数据
│   ├── 1-1.csv
│   └── 1-2.csv
├── plot_speed_data.py        # ← the script shown above / 上述脚本
└── README.md
```

## Main Features | 功能亮点

| EN | 中文 |
|----|------|
|• Plot speed curves for any number of CSV files at once.|• 支持一次性绘制任意数量的 CSV 文件速度曲线。|
|• Auto-interpolation, low-speed cropping, overspeed detection.|• 自动插值、低速片段裁剪、超速检测。|
|• Overspeed points are marked in a darker tone.|• 超速点使用更深颜色标注。|
|• Optional per-file interactive AMap (HTML) with polyline + markers.|• （可选）为每个文件生成独立高德地图 HTML，展示路径及超速点。|
|• All labels rendered in English, font = Times New Roman.|• 图表标签全部英文，字体 Times New Roman。|

## Requirements | 运行环境

- Python ≥ 3.8
- pandas
- matplotlib

Use the following command to install the required Python packages:

使用以下命令安装所需的 Python 包：

```bash
pip install pandas matplotlib
```

## Usage | 使用方法

```bash
# Make sure you are inside the project root
python plot_speed_data.py
```

The script will interactively ask you to:  
1. Choose the CSV files (by number).  
2. Enter a speed-limit value (default 22 km/h).  
3. Optionally paste your AMap API key (press Enter to skip map generation).

脚本会交互式让你：  
1. 选择要绘制的 CSV 文件（按序号）。  
2. 输入速度阈值（默认为 22 km/h）。  
3. （可选）输入高德地图 API Key（回车可跳过地图生成）。

All resulting HTML maps will open automatically in your default browser and are saved as  
`<csv_filename>_map.html`.

所有生成的 HTML 地图会自动在默认浏览器中打开并保存为 `<csv_filename>_map.html`。

## Getting an AMap Web JS API Key | 获取高德地图 Key

1. Register/Login AMap Open Platform: <https://lbs.amap.com/>  
2. Create a new application → choose *Web端(JavaScript)* service.  
3. Copy the generated **Key** and paste it when the script asks for it.  
   (If you skip, only the speed curve will be produced.)

<!-- Split the list -->

1. 注册/登录高德开放平台：<https://lbs.amap.com/>
2. 创建新应用 → 选择 *Web端(JavaScript)* 服务。
3. 复制生成的 **Key** 并粘贴到脚本要求输入的位置。
   （如果跳过，仅绘制速度曲线。）

## Sample CSV Layout | CSV 数据格式示例
| Time | Speed (km/h) | Latitude | Longitude |
|------|--------------|----------|-----------|
| 09:12:01 | 15.2 | 39.90923 | 116.397428 |
| 09:12:02 | 16.8 | 39.90930 | 116.397500 |
| … | … | … | … |

Columns are case-sensitive and must match exactly.  
列名区分大小写，需与脚本中的设定完全一致。


## FAQ

**Q1:** *Why do I only see the speed plot but no map?*  
A1: You pressed Enter when asked for the AMap key, or your CSV lacks latitude/longitude columns.

**Q2:** *How to change the low-speed filter (3 km/h, 5 s)*?  
A2: Edit `low_speed_threshold` and `low_speed_duration_s` near the middle of `plot_speed_data.py`.

**Q1:** *为什么我只看到了速度-时间曲线，但没有地图？* 
A1: 你在输入 AMap Key 的时候按了回车，或者你的 CSV 数据中缺少了经纬度列。

**Q2:** *如何修改低速过滤阈值（3 km/h, 5 s）？*
A2: 编辑 `plot_speed_data.py` 文件中部附近的 `low_speed_threshold` 和 `low_speed_duration_s`。