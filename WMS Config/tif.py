import requests
import datetime
import os

# Configurable parameters
base_url = "http://localhost:8081/geoserver/cloudweave/wms"
layers = "cloudweave:cyc"
bbox = "-3473242.733735,-1058893.6874970002,3473242.733735,5401854.420193"
width = 768
height = 714
srs = "EPSG:4326"
output_format = "image/tiff"
output_directory = "./downloaded_files"
specific_time = "2019-11-03T17:30:00Z"  # 5:30 PM

def download_file(url, output_path):
    """Download a file from a URL and save it to the specified path."""
    response = requests.get(url)
    if response.status_code == 200:
        with open(output_path, "wb") as file:
            file.write(response.content)
        print(f"Downloaded: {output_path}")
    else:
        print(f"Failed to download: {url} | Status Code: {response.status_code}")

# Ensure output directory exists
os.makedirs(output_directory, exist_ok=True)

# Generate the WMS request for the specific time
query_params = {
    "service": "WMS",
    "version": "1.1.0",
    "request": "GetMap",
    "layers": layers,
    "bbox": bbox,
    "width": width,
    "height": height,
    "srs": srs,
    "styles": "",
    "format": output_format,
    "time": specific_time,
}
request_url = f"{base_url}?" + "&".join(f"{key}={value}" for key, value in query_params.items())
output_file = os.path.join(output_directory, f"map_{specific_time.replace(':', '').replace('-', '').replace('T', '_').replace('Z', '')}.tif")

# Download the file
download_file(request_url, output_file)
