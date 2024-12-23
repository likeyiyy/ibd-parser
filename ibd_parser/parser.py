import os
from typing import List, Dict, Any
from .constants import PAGE_SIZE, PageType
from .page import PageHeader, IndexHeader
from .record import Record
from .utils import hex_dump

class IBDFileParser:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.file_size = os.path.getsize(file_path)

    def parse_page_directory(self, page_data: bytes, n_dir_slots: int) -> List[int]:
        directory = []
        page_end = PAGE_SIZE - 8
        for i in range(n_dir_slots):
            slot_offset = page_end - (i + 1) * 2
            slot = struct.unpack('>H', page_data[slot_offset:slot_offset+2])[0]
            directory.append(slot)
        return directory

    def analyze_page(self, page_no: int) -> Dict[str, Any]:
        with open(self.file_path, 'rb') as f:
            f.seek(page_no * PAGE_SIZE)
            page_data = f.read(PAGE_SIZE)

            page_header = PageHeader.parse(page_data)
            result = {
                'page_no': page_no,
                'header': page_header
            }

            if page_header.page_type == PageType.FIL_PAGE_INDEX:
                index_header = IndexHeader.parse(page_data)
                result['index_header'] = index_header

                directory = self.parse_page_directory(
                    page_data,
                    index_header.n_dir_slots
                )
                result['directory'] = directory

                # Parse records...

            return result
