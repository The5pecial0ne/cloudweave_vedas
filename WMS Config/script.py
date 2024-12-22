import os
import shutil

def copy_satellite_image_files(source_directory, destination_directory):
    # Create the destination base directory if it doesn't exist
    os.makedirs(destination_directory, exist_ok=True)

    # Month mapping dictionary
    month_map = {
        'JAN': '01', 'FEB': '02', 'MAR': '03', 'APR': '04',
        'MAY': '05', 'JUN': '06', 'JUL': '07', 'AUG': '08',
        'SEP': '09', 'OCT': '10', 'NOV': '11', 'DEC': '12'
    }

    # Iterate through directories and files in the source directory using os.walk
    for root, dirs, files in os.walk(source_directory):
        # Determine the relative path from the source directory
        relative_path = os.path.relpath(root, source_directory)

        # Create corresponding destination subdirectory
        destination_subdir = os.path.join(destination_directory, relative_path)
        os.makedirs(destination_subdir, exist_ok=True)

        for filename in files:
            # Check if file matches the expected pattern
            if filename.endswith('.tif') and '_' in filename:
                try:
                    # Split the filename
                    parts = filename.split('_')

                    # Find the date part (e.g., 14MAY2019)
                    date_part = next(part for part in parts if any(month in part for month in month_map.keys()))

                    # Find the time part (e.g., 1745)
                    time_part = next(part for part in parts if part.isdigit() and len(part) == 4)

                    # Convert month to number
                    day = date_part[:2]
                    month = month_map[date_part[2:5]]
                    year = date_part[5:]

                    # Format time
                    hour = time_part[:2]
                    minute = time_part[2:]

                    # Create new filename
                    new_filename = f"{year}.{month}.{day}.{hour}.{minute}.tif"

                    # Full paths for source and destination
                    source_path = os.path.join(root, filename)
                    destination_path = os.path.join(destination_subdir, new_filename)

                    # Copy the file
                    shutil.copy2(source_path, destination_path)
                    print(f"Copied: {filename} -> {os.path.join(relative_path, new_filename)}")

                except Exception as e:
                    print(f"Error processing {filename} in {root}: {e}")

# Example usage
# Replace these paths with your actual source and destination directories
source_directory = 'cyc'
destination_directory = 'output'

copy_satellite_image_files(source_directory, destination_directory)