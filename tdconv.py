import csv
import argparse


def convert(args):

    with open(args.file) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            print(row['TYPE'])

def main():
    parser = argparse.ArgumentParser(
        description='Convert todoist template files to other formats.')

    parser.add_argument('--verbose', '-v', action='count', default=0,
                        help='increase level of verbosity (repeat up to 3 times)')
    parser.add_argument('--format', '-f', default='md',
                        help='format of target file: md (later maybe also OPML')

    parser.add_argument('file',
                        help='file to convert')
    
    args = parser.parse_args()
    convert(args)
