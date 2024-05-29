import argparse


def parse_args():
    parser = argparse.ArgumentParser(description='Calculate quality of images in a directory.')
    parser.add_argument('--images_dir', type=str, required=True, help='Directory containing images.')
    parser.add_argument('--num_processed', type=int, help='Number of images to process.', default=None)
    parser.add_argument('--sdk_path', type=str, required=True, help='Path to the 3DiVi Face SDK.')
    parser.add_argument('--modification', type=str, default='assessment',
                        help='Modification for quality assessment.')

    return parser.parse_args()


