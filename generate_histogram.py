import os

import pandas as pd
import matplotlib.pyplot as plt


def generate_histogram(input_file):
    path = str(os.path.join(os.path.dirname(__file__), 'results', input_file))

    if not os.path.exists(path):
        print(f'File {input_file} not found.')
        return

    df = pd.read_csv(path)

    if 'totalScore' in df.columns:
        df['totalScore'].hist(bins=10)
        plt.xlabel('Total Score')
        plt.ylabel('Frequency')
        plt.title('Histogram of Total Scores')
        output_path = os.path.join(os.path.dirname(__file__), 'results', 'total_score_histogram.png')
        plt.savefig(output_path)
        print('Histogram successfully created and saved in', os.path.dirname(output_path))
    else:
        print(f'The totalScore column was not found in the {input_file} file.')


if __name__ == '__main__':
    generate_histogram('result.csv')
