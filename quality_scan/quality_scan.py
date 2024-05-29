import os
import random
import cv2
from sys import platform
from face_sdk_3divi import FacerecService, Config



class ImageCollection:
    def __init__(self, root_dir: str, num_processed: int | None = None) -> None:
        self.root_dir = root_dir
        self.num_processed = num_processed
        self.valid_extensions = {'.png', '.bmp', '.tif', '.tiff', '.jpg', '.jpeg', '.ppm'}

    def find_images(self) -> list[str]:
        images = []
        for root, _, files in os.walk(self.root_dir):
            for file in files:
                if os.path.splitext(file.lower())[1] in self.valid_extensions:
                    images.append(os.path.join(root, file))

        if self.num_processed and len(images) > self.num_processed:
            images = random.sample(images, self.num_processed)

        return images


