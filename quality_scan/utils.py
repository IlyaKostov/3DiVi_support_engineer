import argparse
import os
import pandas as pd
import matplotlib.pyplot as plt


def parse_args() -> argparse.Namespace:
    """
    Parse command-line arguments for the image quality assessment.
    :return: parsed command-line arguments
    """
    parser = argparse.ArgumentParser(description='Calculate quality of images in a directory.')
    parser.add_argument('--images_dir', type=str, required=True, help='Directory containing images.')
    parser.add_argument('--num_processed', type=int, help='Number of images to process.', default=None)
    parser.add_argument('--sdk_path', type=str, required=True, help='Path to the 3DiVi Face SDK.')
    parser.add_argument('--modification', type=str, default='assessment',
                        help='Modification for quality assessment.')

    return parser.parse_args()


def create_histogram(dataframe: pd.DataFrame, output_directory: str) -> None:
    """Create a histogram based on the 'totalScore' column of a DataFrame"""
    dataframe['totalScore'].hist(bins=10)
    plt.xlabel('Total Scores')
    plt.ylabel('Frequency')
    plt.title('Histogram of Total Scores')
    plt.savefig(os.path.join(output_directory, 'total_score_histogram.png'))
    print('Histogram successfully created and saved in', output_directory)
