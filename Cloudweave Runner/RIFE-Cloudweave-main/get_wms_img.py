import os
import requests
from datetime import datetime, timedelta

# GeoServer URL and parameters
base_url = "http://10.10.9.25:8080/geoserver/cloudweave/wcs"
layer_name = "cyc"
srs = "EPSG:4326"
output_format = "image/png"

# Directory to save the images
output_directory = "./input_frames"

# Ensure the output directory exists
os.makedirs(output_directory, exist_ok=True)

def fetch_images(bbox, width, height, start_time, end_time):
    print(start_time, end_time)
        
    labels = {
        1: "2019-05-14T00:15:00.000Z",
        2: "2019-05-14T00:45:00.000Z",
        3: "2019-05-14T01:15:00.000Z",
        4: "2019-05-14T01:45:00.000Z",
        5: "2019-05-14T02:15:00.000Z",
        6: "2019-05-14T02:45:00.000Z",
        7: "2019-05-14T03:15:00.000Z",
        8: "2019-05-14T03:45:00.000Z",
        9: "2019-05-14T04:15:00.000Z"
    }

    start_index = 1
    end_index = 1
    for l in labels.values():
        if(l == start_time):
            break
        else:
            start_index += 1

    for l in labels.values():
        if(l == end_time):
            break
        else:
            end_index += 1
    print(start_index, end_index)
    
    # formatted_start_time = datetime.fromisoformat(start_time)
    # formatted_end_time = datetime.fromisoformat(end_time)
    # print(formatted_start_time, formatted_end_time)
    img_num = 0
    # current_time = formatted_start_time
    
    while start_index <= end_index:
        params = {
            "service": "WMS",
            "version": "1.1.1",
            "request": "GetMap",
            "layers": start_index,
            "bbox": bbox,
            "width": width,
            "height": height,
            "srs": srs,
            "styles": "",
            "format": output_format,
            # "time": time_param,
            "dpi":96,
            "map_resolution":96,
            "transparent":True
        }
                
        # Send the request
        response = requests.get(base_url, params=params)
        print('URL hit:' , response.url)
        if response.status_code == 200:
            filename = os.path.join(output_directory, f"{img_num}.png")
            with open(filename, "wb") as f:
                f.write(response.content)
        else:
            print(f"Failed to fetch image for time {start_index}. Status code: {response.status_code}")
        
        img_num += 1
        start_index += 1

# Run the function
# fetch_images(bbox_input, width_input, height_input, start_time_input, end_time_input, time_step_input)
