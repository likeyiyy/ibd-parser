import argparse
from . import IBDFileParser

def main():
    parser = argparse.ArgumentParser(description='InnoDB IBD file parser')
    parser.add_argument('file', help='Path to .ibd file')
    parser.add_argument('--page', type=int, help='Page number to analyze')
    args = parser.parse_args()

    ibd_parser = IBDFileParser(args.file)
    if args.page is not None:
        result = ibd_parser.analyze_page(args.page)
        print(result)

if __name__ == '__main__':
    main()
