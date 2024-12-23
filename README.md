# InnoDB IBD File Parser

A Python tool for parsing and analyzing InnoDB .ibd files. This tool helps database administrators and developers understand the internal structure of InnoDB tablespace files.

## Features

- Parse InnoDB page headers
- Analyze index pages
- Extract record contents
- Support for various page types:
  - Index pages (B-tree nodes)
  - File space header
  - XDES (Extent descriptor)
  - BLOB pages
  - And more...

## Installation

From PyPI:
```bash
pip install ibd-parser
```

From source:
```bash
pip install git+https://github.com/likeyiyy/ibd-parser.git
```

## Usage

### Command Line Interface

```bash
# Analyze a specific page
ibd-parser analyze /path/to/table.ibd --page 4

# Show page header only
ibd-parser header /path/to/table.ibd --page 4

# Dump records from an index page
ibd-parser records /path/to/table.ibd --page 4

# Show hex dump of a page
ibd-parser hexdump /path/to/table.ibd --page 4 --length 128

# Show summary of the file
ibd-parser info /path/to/table.ibd

# Additional options
ibd-parser analyze /path/to/table.ibd --page 4 --format json  # Output in JSON format
ibd-parser analyze /path/to/table.ibd --page 4 --verbose     # Show detailed information
```

### Python API

```python
from ibd_parser import IBDFileParser

# Initialize parser with your .ibd file
parser = IBDFileParser("/path/to/your/table.ibd")

# Analyze a specific page
page_info = parser.analyze_page(page_no=4)

# Access page information
print(f"Page Type: {page_info['header'].page_type}")
if 'index_header' in page_info:
    print(f"Number of records: {page_info['index_header'].n_recs}")

# Get records from an index page
records = parser.get_records(page_no=4)
for record in records:
    print(record.data)

# Hex dump of a page
parser.hex_dump(page_no=4, length=128)
```

## Project Structure

```
ibd_parser/
├── ibd_parser/
│   ├── __init__.py
│   ├── constants.py    # Constants and enums
│   ├── page.py        # Page structure definitions
│   ├── record.py      # Record parsing
│   ├── parser.py      # Main parser implementation
│   ├── cli.py         # Command line interface
│   └── utils.py       # Utility functions
├── tests/
├── README.md
└── pyproject.toml     # Project metadata and dependencies
```

## Page Structure

An InnoDB page (default 16KB) consists of:

1. File Header (38 bytes)
2. Page Header (56 bytes)
3. Infimum/Supremum Records
4. User Records
5. Free Space
6. Page Directory
7. File Trailer (8 bytes)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Based on the InnoDB storage engine documentation
- Inspired by various InnoDB internals research papers and blog posts

## References

- [InnoDB Page Structure](https://dev.mysql.com/doc/refman/8.0/en/innodb-page-structure.html)
- [InnoDB File Space Management](https://dev.mysql.com/doc/refman/8.0/en/innodb-file-space.html)

## Future Plans

I will continue to enhance this project to make it more practical and valuable. Planned improvements include:

- Support for more page types
- Enhanced record analysis
- Data recovery features
- More comprehensive CLI tools
- Better documentation and examples

Contributions and suggestions are welcome!
