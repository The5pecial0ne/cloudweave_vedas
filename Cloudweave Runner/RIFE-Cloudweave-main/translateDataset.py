import os
import subprocess
from tifffile import imread
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed

class TranslateDataset:
    def __init__(self, translate_command: str = 'gdal_translate', output_format: str = 'JPEG', output_type: str = 'byte', output_extension: str = 'jpg', max_threads: int = 4):
        if output_format != 'JPEG' and output_extension == 'jpg':
            raise ValueError("output_extension should be set if output_format is not JPEG")

        self.translate_command = translate_command
        self.output_format = output_format
        self.output_type = output_type
        self.output_extension = output_extension
        self.max_threads = max_threads
        self.min_val = None
        self.max_val = None

    def min_percentile(self, arr: np.ndarray):
        return np.percentile(arr.flatten(), 2)

    def max_percentile(self, arr: np.ndarray):
        return np.percentile(arr.flatten(), 98)

    def output_file_name(self, input_file: str):
        return os.path.splitext(input_file)[0] + '.' + self.output_extension

    def translate_file(self, input_file: str, output_file: str, min_val: float, max_val: float):
        print(f"Processing {input_file} -> {output_file}")
        cmd = f"{self.translate_command} {input_file} {output_file} -of {self.output_format} -ot byte -scale {min_val} {max_val} 0 255 -a_nodata 0"
        subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE)

    def compute_global_min_max(self, input_dir: str):
        min_vals = []
        max_vals = []
        tasks = []
        with ThreadPoolExecutor(max_workers=self.max_threads) as executor:
            for file in os.listdir(input_dir):
                if file.endswith('.tif'):
                    input_file = os.path.join(input_dir, file)
                    tasks.append(executor.submit(self.compute_min_max_for_file, input_file))
            
            for future in as_completed(tasks):
                try:
                    min_val, max_val = future.result()
                    min_vals.append(min_val)
                    max_vals.append(max_val)
                except Exception as e:
                    print(f"Error processing file for min/max calculation: {e}")

        self.min_val = min(min_vals)
        self.max_val = max(max_vals)
        print(f"Computed global min_val: {self.min_val}, max_val: {self.max_val}")

    def compute_min_max_for_file(self, file: str):
        ras = imread(file)
        return self.min_percentile(ras), self.max_percentile(ras)

    def translate_dir(self, input_dir: str, output_dir: str):
        os.makedirs(output_dir, exist_ok=True)

        # Compute global min and max values
        self.compute_global_min_max(input_dir)

        tasks = []
        with ThreadPoolExecutor(max_workers=self.max_threads) as executor:
            for file in os.listdir(input_dir):
                if file.endswith('.tif'):
                    input_file = os.path.join(input_dir, file)
                    output_file = os.path.join(output_dir, self.output_file_name(file))

                    # Submit task with precomputed global min and max values
                    tasks.append(executor.submit(self.translate_file, input_file, output_file, self.min_val, self.max_val))
            
            for future in as_completed(tasks):
                try:
                    future.result()
                except Exception as e:
                    print(f"Error processing file: {e}")