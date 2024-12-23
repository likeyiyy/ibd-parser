from dataclasses import dataclass
import struct
from typing import Dict, Any, List
from .constants import PageType, PAGE_SIZE, FIL_PAGE_DATA

@dataclass
class PageHeader:
    checksum: int
    page_no: int
    previous_page: int
    next_page: int
    lsn: int
    page_type: PageType
    flush_lsn: int
    space_id: int

    @classmethod
    def parse(cls, page_data: bytes) -> 'PageHeader':
        header = struct.unpack('>IIIIQHQI', page_data[:38])
        return cls(
            checksum=header[0],
            page_no=header[1],
            previous_page=header[2],
            next_page=header[3],
            lsn=header[4],
            page_type=PageType(header[5]),
            flush_lsn=header[6],
            space_id=header[7]
        )

@dataclass
class IndexHeader:
    n_dir_slots: int
    heap_top: int
    n_heap: int
    format: str
    garbage_offset: int
    garbage_size: int
    last_insert_offset: int
    direction: str
    n_direction: int
    n_recs: int
    max_trx_id: int
    level: int
    index_id: int

    @classmethod
    def parse(cls, page_data: bytes) -> 'IndexHeader':
        offset = FIL_PAGE_DATA
        header = struct.unpack('>HHHHHHHHHQHQ', page_data[offset:offset+36])

        n_heap_format = header[2]
        format_flag = (n_heap_format & 0x8000) >> 15
        n_heap = n_heap_format & 0x7fff

        direction = "no_direction"
        if header[6] == 1:
            direction = "right"
        elif header[6] == 2:
            direction = "left"

        return cls(
            n_dir_slots=header[0],
            heap_top=header[1],
            n_heap=n_heap,
            format="compact" if format_flag == 1 else "redundant",
            garbage_offset=header[3],
            garbage_size=header[4],
            last_insert_offset=header[5],
            direction=direction,
            n_direction=header[7],
            n_recs=header[8],
            max_trx_id=header[9],
            level=header[10],
            index_id=header[11]
        )
