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

    def min_percentile(self, arr: np.ndarray):
        return np.percentile(arr.flatten(), 2)

    def max_percentile(self, arr: np.ndarray):
        return np.percentile(arr.flatten(), 98)

    def output_file_name(self, input_file: str):
        return os.path.splitext(input_file)[0] + '.jpg'

    def translate_file(self, input_file: str, output_file: str):
        ras = imread(input_file)
        min_val = self.min_percentile(ras)
        max_val = self.max_percentile(ras)
        print(f"Processing {input_file} -> {output_file}")
        cmd = f"{self.translate_command} {input_file} {output_file} -of JPEG -ot byte -scale {min_val} {max_val} 0 255 -a_nodata 0"
        subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE)

    def translate_dir(self, input_dir: str, output_dir: str):
        os.makedirs(output_dir, exist_ok=True)
        tasks = []
        with ThreadPoolExecutor(max_workers=self.max_threads) as executor:
            for file in os.listdir(input_dir):
                if file.endswith('.tif'):
                    input_file = os.path.join(input_dir, file)
                    output_file = os.path.join(output_dir, self.output_file_name(file))
                    tasks.append(executor.submit(self.translate_file, input_file, output_file))
            for future in as_completed(tasks):
                try:
                    future.result()
                except Exception as e:
                    print(f"Error processing file: {e}")

