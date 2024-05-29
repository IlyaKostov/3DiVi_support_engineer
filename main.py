import os

import pandas as pd
from alive_progress import alive_bar
from quality_scan.scanner import ImageCollection, ImageQualityAssessor
from quality_scan.utils import parse_args


def main():
    args = parse_args()
    images = ImageCollection(args.images_dir, args.num_processed).find_images()
    assessor = ImageQualityAssessor(args.sdk_path, args.modification)
    results = []
    with alive_bar(len(images)) as progress:
        for image_path in images:
            result = assessor.assess_image(image_path)
            if result:
                results.append(result)
                progress()

    df = pd.DataFrame(results)

    output_directory = 'results'
    os.makedirs(output_directory, exist_ok=True)

    df.to_csv(os.path.join(output_directory, 'result.csv'), index=False)
    print('Quality assessment completed and save in', output_directory)


if __name__ == "__main__":
    main()
