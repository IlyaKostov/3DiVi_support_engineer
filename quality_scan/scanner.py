import os
import random
import sys

import cv2
from sys import platform
from face_sdk_3divi import FacerecService, Config, Capturer, Error
from face_sdk_3divi.modules.context import Context
from face_sdk_3divi.modules.processing_block import ProcessingBlock


class ImageCollection:
    """Find Collection of images in special directory and return a list of them"""

    def __init__(self, root_dir: str, num_processed: int | None = None) -> None:
        self.root_dir = root_dir
        self.num_processed = num_processed
        self.valid_extensions: set[str] = {'.png', '.bmp', '.tif', '.tiff', '.jpg', '.jpeg', '.ppm'}

    def find_images(self) -> list[str]:
        """
        Find images in the specified directory
        """
        images: list[str] = []
        for root, _, files in os.walk(self.root_dir):
            for file in files:
                if os.path.splitext(file.lower())[1] in self.valid_extensions:
                    images.append(os.path.join(root, file))

        if self.num_processed and len(images) > self.num_processed:
            images = random.sample(images, self.num_processed)

        return images


class ImageQualityAssessor:
    """Class for assessing the quality of an image using SDK functions"""

    def __init__(self, sdk_path: str, modification: str) -> None:
        self.sdk_path = sdk_path
        self.modification = modification
        self.service: FacerecService = self._create_service()
        self.quality_block: ProcessingBlock = self._create_quality_block()
        self.capturer: Capturer = self._create_capturer()
        self.sdk_onnx_path: str | None = None

    def _create_service(self) -> FacerecService:
        """Create and return a FacerecService instance"""
        sdk_conf_dir: str = os.path.join(self.sdk_path, 'conf', 'facerec')
        if platform == 'win32':  # for Windows
            sdk_dll_path: str = os.path.join(self.sdk_path, 'bin', 'facerec.dll')
            self.sdk_onnx_path = os.path.join(self.sdk_path, 'bin')
        else:  # for Linux
            sdk_dll_path: str = os.path.join(self.sdk_path, 'lib', 'libfacerec.so')
            self.sdk_onnx_path = os.path.join(self.sdk_path, 'lib')
        try:
            service = FacerecService.create_service(
                sdk_dll_path,
                sdk_conf_dir,
                f'{self.sdk_path}/license'
            )
        except FileNotFoundError as e:
            print(f'{e} Try checking the sdk_path')
            sys.exit(1)
        return service

    def _create_quality_block(self) -> ProcessingBlock:
        """Create and return a quality block"""
        quality_config: dict[str, str | dict[str, str | None]] = {
            'unit_type': 'QUALITY_ASSESSMENT_ESTIMATOR',
            'modification': self.modification,
            'ONNXRuntime': {'library_path': self.sdk_onnx_path}
        }
        if self.modification == 'assessment':
            quality_config['config_name'] = 'quality_assessment.xml'
        try:
            quality_block = self.service.create_processing_block(quality_config)
        except Error:
            print(f'Unknown modification {self.modification} for QUALITY_ASSESSMENT_ESTIMATOR')
            sys.exit(1)
        return quality_block

    def _create_capturer(self) -> Capturer:
        """Create and return a capturer"""
        capturer_config = Config('common_capturer_uld_fda.xml')
        return self.service.create_capturer(capturer_config)

    def assess_image(self, image_path: str) -> dict | None:
        """
        Assess the quality of an image and return the assessment results
        :return: dictionary containing image quality assessment results or None
        """
        img = cv2.imread(image_path, cv2.IMREAD_COLOR)
        image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        _, im_png = cv2.imencode('.png', image)
        img_bytes: bytes = im_png.tobytes()

        image_name: str = os.path.basename(image_path)

        samples = self.capturer.capture(img_bytes)

        image_ctx: dict[str, str | bytes | list[int]] = {
            'blob': image.tobytes(),
            'dtype': 'uint8_t',
            'format': 'NDARRAY',
            'shape': [dim for dim in image.shape]
        }

        ioData: Context = self.service.create_context({'image': image_ctx})
        ioData['objects'] = []

        for sample in samples:
            ctx: Context = sample.to_context()
            ioData['objects'].push_back(ctx)

        self.quality_block(ioData)

        if ioData['objects']:
            obj: Context = ioData['objects'][0]
            if self.modification == 'assessment':
                return {
                    'filename': image_name,
                    'confidence': '{:.2f}'.format(round(obj['confidence'].get_value(), 2)),
                    'totalScore': int(obj['quality']['total_score'].get_value() * 100),
                    'isSharp': int(obj['quality']['is_sharp'].get_value()),
                    'sharpnessScore': int(obj['quality']['sharpness_score'].get_value() * 100),
                    'isEvenlyIlluminated': int(obj['quality']['is_evenly_illuminated'].get_value()),
                    'illuminationScore': int(obj['quality']['illumination_score'].get_value() * 100),
                    'noFlare': int(obj['quality']['no_flare'].get_value()),
                    'isLeftEyeOpened': int(obj['quality']['is_left_eye_opened'].get_value()),
                    'isRightEyeOpened': int(obj['quality']['is_right_eye_opened'].get_value()),
                    'isRotationAcceptable': int(obj['quality']['is_rotation_acceptable'].get_value()),
                    'notMasked': int(obj['quality']['not_masked'].get_value()),
                    'isNeutralEmotion': int(obj['quality']['is_neutral_emotion'].get_value()),
                    'isEyesDistanceAcceptable': int(obj['quality']['is_eyes_distance_acceptable'].get_value()),
                    'eyesDistance': obj['quality']['eyes_distance'].get_value(),
                    'isMarginsAcceptable': int(obj['quality']['is_margins_acceptable'].get_value()),
                    'isNotNoisy': int(obj['quality']['is_not_noisy'].get_value()),
                    'hasWatermark': int(obj['quality']['has_watermark'].get_value()),
                    'dynamicRangeScore': int(obj['quality']['dynamic_range_score'].get_value() * 100),
                    'isDynamicRangeAcceptable': int(obj['quality']['is_dynamic_range_acceptable'].get_value())
                }
            elif self.modification == 'estimation':
                return {
                    'filename': image_name,
                    'totalScore': int(obj['quality']['total_score'].get_value() * 100)
                }
        return None
