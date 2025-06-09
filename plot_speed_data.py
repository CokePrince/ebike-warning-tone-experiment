import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker # Import ticker
import matplotlib.colors as mcolors # Import mcolors for color manipulation
import webbrowser
import json # For embedding data in HTML

def plot_data_from_csv():
    """
    读取指定CSV文件中的数据，并绘制速度曲线，高亮显示超速部分。
    为每个CSV文件生成一个独立的HTML地图。
    图表元素使用英文，并设置字体为Times New Roman。
    """
    # 设置Matplotlib字体
    plt.rcParams['font.family'] = 'Times New Roman'
    plt.rcParams['axes.unicode_minus'] = False # 正确显示负号


    # 1. 读取当前目录下的csv文件夹
    csv_dir = 'csv'
    if not os.path.isdir(csv_dir):
        print(f"Error: Directory '{csv_dir}' not found. Please ensure it exists in the current path.")
        return

    csv_files = [f for f in os.listdir(csv_dir) if f.endswith('.csv')]

    if not csv_files:
        print(f"Error: No CSV files found in '{csv_dir}' directory.")
        return

    print("Available CSV files:")
    for i, filename in enumerate(csv_files):
        print(f"{i + 1}. {filename}")

    # 2. 用户指定待绘制数据表文件的文件名 (支持多个文件)
    selected_files_info = []
    while True:
        try:
            file_indices_str = input(f"Enter the numbers of the CSV files to plot (1-{len(csv_files)}), separated by commas: ")
            if not file_indices_str:
                print("No file selected. Please enter at least one number.")
                continue
            indices = [int(i.strip()) - 1 for i in file_indices_str.split(',')]
            
            valid_indices = True
            temp_selected_files = []
            for index in indices:
                if 0 <= index < len(csv_files):
                    temp_selected_files.append({'name': csv_files[index], 'path': os.path.join(csv_dir, csv_files[index])})
                else:
                    print(f"Invalid input: {index + 1} is not a valid file number. Please enter numbers between 1 and {len(csv_files)}.")
                    valid_indices = False
                    break
            if valid_indices and temp_selected_files:
                selected_files_info = temp_selected_files
                break
            elif not temp_selected_files:
                 print("No valid files selected.")
        except ValueError:
            print("Invalid input. Please enter numbers separated by commas.")
        except EOFError:
            print("\nOperation cancelled.")
            return

    if not selected_files_info:
        print("No files selected for plotting.")
        return

    # 3. 用户指定速度限值，默认22
    while True:
        try:
            speed_limit_str = input("Enter the speed limit (default is 22): ")
            if not speed_limit_str:
                speed_limit = 22.0
                break
            speed_limit = float(speed_limit_str)
            if speed_limit > 0:
                break
            else:
                print("Speed limit must be greater than 0.")
        except ValueError:
            print("Invalid input. Please enter a number.")
        except EOFError:
            print("\nOperation cancelled.")
            return

    time_col = 'Time'
    speed_col = 'Speed (km/h)'
    lat_col = 'Latitude'
    lon_col = 'Longitude'
    relative_time_col = 'Riding Time (s)'

    # 4. 绘图和地图数据准备
    plt.figure(figsize=(12, 6))
    
    try:
        cmap = plt.colormaps.get_cmap('tab10') 
    except AttributeError:
        cmap = plt.cm.get_cmap('tab10') 
    
    if hasattr(cmap, 'colors'):
        num_unique_colors = len(cmap.colors)
        def get_plot_color(index):
            return cmap.colors[index % num_unique_colors]
    else: 
        num_unique_colors = 10 
        def get_plot_color(index):
            return cmap( (index % num_unique_colors) / float(num_unique_colors) ) # Ensure float division

    # Prompt for AMap API key for map generation at the beginning
    amap_api_key_input = input("Enter your AMap API key (press Enter to skip map generation): ").strip()
    maps_enabled = bool(amap_api_key_input)

    any_file_has_plottable_data = False # Flag to check if any data is actually plotted

    for idx, file_info in enumerate(selected_files_info):
        file_path = file_info['path']
        selected_file_name = os.path.splitext(file_info['name'])[0] # e.g., "data1.csv"
        print(f"\nProcessing file: {selected_file_name}")

        try:
            data = pd.read_csv(file_path)
        except FileNotFoundError:
            print(f"Error: File '{file_path}' not found.")
            continue
        except pd.errors.EmptyDataError:
            print(f"Error: File '{file_path}' is empty.")
            continue
        except Exception as e:
            print(f"Error reading CSV file '{file_path}': {e}")
            continue

        required_cols = [time_col, speed_col, lat_col, lon_col]
        missing_cols = [col for col in required_cols if col not in data.columns]
        if missing_cols:
            print(f"Error: CSV file '{selected_file_name}' is missing required columns: {', '.join(missing_cols)}.")
            print(f"Columns in '{selected_file_name}': {data.columns.tolist()}")
            continue

        try:
            data[time_col] = pd.to_datetime(data[time_col], format='%H:%M:%S')
        except ValueError as e:
            print(f"Error converting 'Time' column to datetime in '{selected_file_name}': {e}. Ensure time is in HH:MM:SS format.")
            continue
        
        if data.empty: # Check after loading, before processing
            print(f"Warning: File '{selected_file_name}' is empty or became empty after initial read.")
            continue

        data = data.set_index(time_col)
        data = data.resample('1s').asfreq() 
        data[speed_col] = data[speed_col].interpolate(method='linear')
        
        if lat_col in data.columns:
            data[lat_col] = data[lat_col].interpolate(method='linear')
        if lon_col in data.columns:
            data[lon_col] = data[lon_col].interpolate(method='linear')
        data = data.reset_index() 

        data.dropna(subset=[speed_col, lat_col, lon_col], inplace=True)
        if data.empty:
            print(f"No valid data after initial load and interpolation for '{selected_file_name}'.")
            continue

        low_speed_threshold = 3  
        low_speed_duration_s = 5 

        # Filter start low speed
        first_valid_index = 0
        if not data.empty:
            for i in range(len(data) - low_speed_duration_s + 1):
                window = data[speed_col].iloc[i : i + low_speed_duration_s]
                if not (window <= low_speed_threshold).all():
                    first_valid_index = i
                    break
            else: 
                first_valid_index = len(data)
            data = data.iloc[first_valid_index:].copy()
        
        # Filter end low speed
        last_valid_index = len(data)
        if not data.empty:
            for i in range(len(data) -1, low_speed_duration_s - 2, -1):
                window = data[speed_col].iloc[i - low_speed_duration_s + 1 : i + 1]
                if not (window <= low_speed_threshold).all():
                    last_valid_index = i + 1
                    break
            else: 
                last_valid_index = 0
            data = data.iloc[:last_valid_index].copy()

        if data.empty:
            print(f"No data remaining for '{selected_file_name}' after filtering low-speed segments.")
            continue
        
        # If we reach here, data is valid for this file
        any_file_has_plottable_data = True 

        start_time = data[time_col].iloc[0]
        data[relative_time_col] = (data[time_col] - start_time).dt.total_seconds()
        
        current_plot_color = get_plot_color(idx)
        plt.plot(data[relative_time_col], data[speed_col], label=f'Speed ({selected_file_name})', color=current_plot_color)

        exceeding_speed = data[data[speed_col] > speed_limit]
        if not exceeding_speed.empty:
            rgba_color = mcolors.to_rgba(current_plot_color)
            darker_color = (rgba_color[0] * 0.7, rgba_color[1] * 0.7, rgba_color[2] * 0.7, rgba_color[3])
            plt.scatter(exceeding_speed[relative_time_col], exceeding_speed[speed_col], color=darker_color, marker='.', label=f'Overspeed ({selected_file_name})', zorder=5)

        path_coords = []
        if not data.empty and lat_col in data.columns and lon_col in data.columns:
            path_coords = data[[lon_col, lat_col]].values.tolist()
        
        overspeed_coords = []
        if not exceeding_speed.empty and lat_col in exceeding_speed.columns and lon_col in exceeding_speed.columns:
            overspeed_coords = exceeding_speed[[lon_col, lat_col]].values.tolist()
        
        # Generate individual map for this file
        if maps_enabled and (path_coords or overspeed_coords): 
            generate_map_html(
                file_name=selected_file_name, 
                path_coords=path_coords,
                overspeed_coords=overspeed_coords,
                plot_color_hex=mcolors.to_hex(current_plot_color),
                api_key=amap_api_key_input
            )
        elif not maps_enabled and (path_coords or overspeed_coords):
            print(f"Skipping individual map generation for {selected_file_name} as API key was not provided.")
        else:
            print(f"No coordinate data (path or overspeed) to generate map for {selected_file_name}.")

    # After processing all files, finalize and show the plot if any data was plotted
    if not any_file_has_plottable_data:
        print("No data to plot after processing all selected files.")
        plt.close() # Close the empty figure
        return

    plt.xlabel(relative_time_col) 
    plt.ylabel('Speed (km/h)')
    plt.title('Speed Over Time') 
    plt.axhline(y=speed_limit, color='gray', linestyle='--', label=f'Speed Limit ({speed_limit} km/h)')
    
    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict(zip(labels, handles)) 
    plt.legend(by_label.values(), by_label.keys())
    
    plt.grid(True)

    ax = plt.gca()
    ax.xaxis.set_major_locator(ticker.MaxNLocator(nbins=10))
    plt.xticks(rotation=0, ha='center') 

    plt.tight_layout()
    plt.show()

    # 5. 生成地图HTML文件 (This section for combined map might need adjustment or removal if individual maps are preferred)
    # For now, let's assume the primary goal was individual maps. 
    # If a combined map is still desired, it should also check 'maps_enabled'.
    # The existing logic for 'all_files_coords_data' and its use for a combined map is a bit unclear
    # with the introduction of per-file map generation. This might need further clarification.
    # For this fix, I'll focus on making individual maps work correctly with the early API key input.

    # Commenting out the combined map generation part as it's now handled per file, 
    # and its logic with 'all_files_coords_data' might conflict or be redundant.
    # if maps_enabled and all_files_coords_data:
    #     # Determine a base name for the HTML file, e.g., from the first selected file or a generic name
    #     # This ensures that even if multiple files are selected, the HTML name is consistent or indicative.
    #     first_file_basename = os.path.splitext(selected_files_info[0]['name'])[0]
    #     generate_map_html(all_files_coords_data, amap_api_key_input, first_file_basename) # This function signature is different now
    # elif not maps_enabled and all_files_coords_data:
    #     print("Skipping combined map generation as API key was not provided.")
    # else:
    #     print("No data suitable for combined map generation was processed.")

def generate_map_html(file_name, path_coords, overspeed_coords, plot_color_hex, api_key):
    """
    Generates an HTML file with an AMap to display the path and overspeeding points for a single file.
    """
    csv_filename_no_ext = os.path.splitext(file_name)[0]
    map_title = f"Driving Path for {file_name}"
    html_filename = f"{csv_filename_no_ext}_map.html"

    all_lons = [lon for lon, lat in path_coords]
    all_lats = [lat for lon, lat in path_coords]
    # Add overspeed coordinates to bounds calculation if path is empty but overspeed exists
    if not all_lons and overspeed_coords:
        all_lons.extend([lon for lon, lat in overspeed_coords])
        all_lats.extend([lat for lon, lat in overspeed_coords])

    center_lon = sum(all_lons) / len(all_lons) if all_lons else 116.397428 
    center_lat = sum(all_lats) / len(all_lats) if all_lats else 39.90923 

    polyline_js = ""
    if path_coords:
        path_coords_js = json.dumps(path_coords)
        polyline_js = f"""
            var path = {path_coords_js};
            var polyline = new AMap.Polyline({{
                'path': path,
                'strokeColor': '{plot_color_hex}',
                'strokeOpacity': 1.0,
                'strokeWeight': 6,
                'strokeStyle': 'solid',
                'strokeDasharray': [10, 5]
            }});
            map.add(polyline);
        """

    overspeed_markers_js = ""
    if overspeed_coords:
        overspeed_coords_js = json.dumps(overspeed_coords)
        overspeed_markers_js = f"""
            var overspeedPoints = {overspeed_coords_js};
            overspeedPoints.forEach(function(point) {{
                var icon = new AMap.Icon({{
                    'size': new AMap.Size(15, 22), 
                    'image': 'https://a.amap.com/jsapi_demos/static/demo-center/icons/poi-marker-red.png',
                    'imageSize': new AMap.Size(15, 22), 
                    'offset': new AMap.Pixel(-7, -22) 
                }});
                var marker = new AMap.Marker({{
                    'position': new AMap.LngLat(point[0], point[1]),
                    'icon': icon, 
                    'offset': new AMap.Pixel(-7, -22) 
                }});
                map.add(marker);
            }});
        """

    html_content = f"""
    <!doctype html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="viewport" content="initial-scale=1.0, user-scalable=no, width=device-width">
        <title>{map_title}</title>
        <link rel="stylesheet" href="https://a.amap.com/jsapi_demos/static/demo-center/css/demo-center.css" />
        <style>
            html, body, #container {{ height: 100%; width: 100%; margin: 0; padding: 0; }}
        </style>
    </head>
    <body>
        <div id="container"></div>
        <script type="text/javascript" src="https://webapi.amap.com/maps?v=2.0&key={api_key}"></script>
        <script type="text/javascript">
            var map = new AMap.Map('container', {{
                'resizeEnable': true,
                'center': [{center_lon}, {center_lat}], 
                'zoom': 12 
            }});

            {polyline_js}
            {overspeed_markers_js}

            var hasPathData = {json.dumps(bool(path_coords))};
            var hasOverspeedData = {json.dumps(bool(overspeed_coords))};

            if (hasPathData || hasOverspeedData) {{
                map.setFitView(); // AMap will fit all overlays on the map
            }}
        </script>
    </body>
    </html>
    """

    try:
        with open(html_filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"Map generated: {html_filename}")
        webbrowser.open('file://' + os.path.realpath(html_filename))
    except Exception as e:
        print(f"Error writing HTML file '{html_filename}': {e}")


if __name__ == "__main__":
    plot_data_from_csv()