#!/usr/bin/env python3

import os
import struct
from enum import IntEnum
from typing import BinaryIO, Dict, Any, List
import json

DATETIME_EPOCH_YEAR = 1970

def parse_datetime(value: int):
    # 秒: 最低6位 (0-63)
    second = value & 0x3F          # 0x3F = 63 = 2^6 - 1
    value = value >> 6

    # 分钟: 最低6位 (0-63)
    minute = value & 0x3F          # 0x3F = 63 = 2^6 - 1
    value = value >> 6

    # 小时: 接下来5位 (0-31)
    hour = value & 0x1F
    value = value >> 5

    # 日: 接下来5位 (0-31)
    day = value & 0x1F
    value = value >> 5

    # 月: 接下来3位 (0-7)
    month = (value % 13 + 3) % 13
    if value % 13 >= 11:
        year = value // 13 + 1970
    else:
        year = value // 13 + 1970 - 1

    return f"{year:04d}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:02d}"

class PageType(IntEnum):
    FIL_PAGE_TYPE_ALLOCATED = 0          # 新分配的页
    FIL_PAGE_TYPE_UNDO_LOG = 2          # Undo日志页
    FIL_PAGE_TYPE_INODE = 3             # 索引节点页
    FIL_PAGE_TYPE_IBUF_FREE_LIST = 4    # Insert buffer空闲列表
    FIL_PAGE_TYPE_IBUF_BITMAP = 5       # Insert buffer位图
    FIL_PAGE_TYPE_SYS = 6               # 系统页
    FIL_PAGE_TYPE_TRX_SYS = 7           # 事务系统数据
    FIL_PAGE_TYPE_FSP_HDR = 8           # 表空间头页
    FIL_PAGE_TYPE_XDES = 9              # 区描述页
    FIL_PAGE_TYPE_BLOB = 10             # Uncompressed BLOB页
    FIL_PAGE_SDI = 17853                # 表空间SDI索引页 (0x45BD)
    FIL_PAGE_RTREE = 17854              # R-tree节点 (0x45BE)
    FIL_PAGE_INDEX = 17855              # B-tree节点 (0x45BF)

    @classmethod
    def _missing_(cls, value):
        """处理未知的页面类型"""
        # 尝试交换字节序
        swapped = ((value & 0xFF) << 8) | ((value & 0xFF00) >> 8)
        if swapped in cls._value2member_map_:
            return cls._value2member_map_[swapped]
        print(f"Warning: Unknown page type: {swapped} (0x{swapped:x})")
        return cls.FIL_PAGE_TYPE_ALLOCATED

    @classmethod
    def get_name(cls, value: int) -> str:
        """获取页类型的可读名称"""
        try:
            return cls(value).name
        except ValueError:
            return f"UNKNOWN_TYPE_{value} (0x{value:04x})"

class IBDFileParser:
    PAGE_SIZE = 16384
    FIL_PAGE_OFFSET = 38        # 文件页头部大小
    FIL_PAGE_DATA = 38          # 添加这个常量

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.file_size = os.path.getsize(file_path)

    def hex_dump(self, data: bytes, start: int = 0, length: int = 64) -> None:
        """打印十六进制数据"""
        for i in range(0, min(length, len(data)), 16):
            # 打印偏移量
            print(f'{start+i:04x}: ', end='')

            # 打印十六进制数据
            hex_data = ' '.join(f'{b:02x}' for b in data[i:i+16])
            print(f'{hex_data:<48}', end='  ')

            # 打印ASCII数据
            ascii_data = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in data[i:i+16])
            print(ascii_data)

    def parse_page_header(self, page_data: bytes) -> Dict[str, Any]:
        """解析页面头部"""
        # 全部使用大端序('>')
        header = struct.unpack('>IIIIQHQI', page_data[:38])

        return {
            'checksum': header[0],
            'page_no': header[1],
            'previous_page': header[2],
            'next_page': header[3],
            'lsn': header[4],
            'page_type': header[5],
            'flush_lsn': header[6],
            'space_id': header[7]
        }

    def print_page_header(self, header: Dict[str, Any]) -> None:
        """打印页头信息"""
        print("Page Header:")
        print(f"checksum: {header['checksum']}")
        print(f"page_no: {header['page_no']}")
        print(f"previous_page: {header['previous_page']}")
        print(f"next_page: {header['next_page']}")
        print(f"lsn: {header['lsn']}")
        print(f"page_type: {header['page_type']}")
        print(f"space_id: {header['space_id']}")

    def parse_index_header(self, page_data: bytes) -> Dict[str, Any]:
        """解析索引头部"""
        offset = self.FIL_PAGE_DATA  # 38
        header = struct.unpack('>HHHHHHHHHQHQ', page_data[offset:offset+36])

        n_heap_format = header[2]
        format_flag = (n_heap_format & 0x8000) >> 15
        n_heap = n_heap_format & 0x7fff

        direction = "no_direction"
        if header[6] == 1:
            direction = "right"
        elif header[6] == 2:
            direction = "left"

        return {
            'n_dir_slots': header[0],
            'heap_top': header[1],
            'n_heap_format': n_heap_format,
            'n_heap': n_heap,
            'format': "compact" if format_flag == 1 else "redundant",
            'garbage_offset': header[3],
            'garbage_size': header[4],
            'last_insert_offset': header[5],
            'direction': direction,
            'n_direction': header[7],
            'n_recs': header[8],
            'max_trx_id': header[9],
            'level': header[10],
            'index_id': header[11]
        }

    def print_index_header(self, header: Dict[str, Any]) -> None:
        """打印索引头部信息"""
        print("#<struct Innodb::Page::Index::PageHeader")
        print(f" n_dir_slots={header['n_dir_slots']},")
        print(f" heap_top={header['heap_top']},")
        print(f" n_heap_format={header['n_heap_format']},")
        print(f" n_heap={header['n_heap']},")
        print(f" format=:{header['format']},")
        print(f" garbage_offset={header['garbage_offset']},")
        print(f" garbage_size={header['garbage_size']},")
        print(f" last_insert_offset={header['last_insert_offset']},")
        print(f" direction=:{header['direction']},")
        print(f" n_direction={header['n_direction']},")
        print(f" n_recs={header['n_recs']},")
        print(f" max_trx_id={header['max_trx_id']},")
        print(f" level={header['level']},")
        print(f" index_id={header['index_id']}>")

    def format_direction(self, direction: int) -> str:
        """将方向值转换为可读字符串"""
        if direction == 1:
            return "right"
        elif direction == 2:
            return "left"
        else:
            return "unknown"

    def parse_record_header(self, page_data: bytes, offset: int) -> Dict[str, Any]:
        """解析记录头信息 (5字节)
        Record Header 格式 (从N-5到N):
        N-5: Info Flags (4 bits) + Number of Records Owned (4 bits)
        N-4: Order (13 bits) 的高8位
        N-3: Order剩余5位 + Record Type (3 bits)
        N-2,N-1: Next Record Offset (2 bytes)
        """
        # 前3个字节包含了所有的位字段
        byte1, byte2, byte3, next_ptr = struct.unpack('>3BH', page_data[offset-5:offset])

        # 解析第一个字节 (8 bits)
        delete_mark = (byte1 >> 7) & 0x01        # 最高位
        min_rec_flag = (byte1 >> 6) & 0x01       # 第二高位
        n_owned = (byte1) & 0x0F            # 后4位


        # heap_no跨越了第2、3个字节 (13 bits)
        heap_no = (byte2 << 5) | (byte3 >> 3)

        record_type = byte3 & 0x07               # 最低3位(实际只用了后3位)

        record_type = "conventional"
        if offset == 99:  # Infimum record
            record_type = "infimum"
        elif offset == 112:  # Supremum record
            record_type = "supremum"

        return {
            'delete_mark': delete_mark,
            'min_rec_flag': min_rec_flag,
            'n_owned': n_owned,
            'record_type': record_type,
            'heap_no': heap_no,
            'next': (offset + next_ptr) % 65536,
        }

    def parse_records(self, page_data: bytes, directory: List[int]) -> List[Dict[str, Any]]:
        """解析所有记录"""
        records = []

        # 首先解析系统记录
        infimum = self.parse_record_header(page_data, directory[0])
        supremum = self.parse_record_header(page_data, directory[-1])
        # 从Infimum开始遍历记录链表
        next_offset = infimum['next']
        while next_offset != supremum['next']:
            record = self.parse_record(page_data, next_offset)
            records.append(record)
            next_offset = record['header']['next']

        return records

    def parse_record(self, page_data: bytes, offset: int) -> Dict[str, Any]:
        """解析记录"""
        data_offset = offset

        header = self.parse_record_header(page_data, data_offset)
        header_offset = data_offset - 5

        # 解析我们的表结构 (users表)
        try:
            # NULL值标志位图
            null_flags_offset = header_offset - 1
            null_flags = page_data[null_flags_offset]


            # 变长字段长度列表 (name和email是变长的)
            var_lens = []
            null_flags_offset -= 1
            for _ in range(2):  # 2个变长字段
                if page_data[null_flags_offset] < 128:  # 1字节长度
                    var_lens.append(page_data[null_flags_offset])
                    null_flags_offset -= 1
                else:  # 2字节长度
                    var_lens.append(((page_data[null_flags_offset] & 0x3F) << 8) | page_data[null_flags_offset + 1])
                    null_flags_offset -= 2
            # 解析固定长度字段
            id_value = struct.unpack('>I', page_data[data_offset:data_offset+4])[0]
            id_value = id_value & ~0x80000000
            data_offset += 4

            # 解析事务ID
            trx_id_offset = data_offset
            trx_id_bytes = page_data[trx_id_offset:trx_id_offset+6]
            # 补充2个字节的0以满足8字节长度
            trx_id_bytes = b'\x00\x00' + trx_id_bytes
            trx_id_value = struct.unpack('>Q', trx_id_bytes)[0]
            data_offset += 6

            # 解析回滚指针
            rollback_pointer_offset = data_offset
            rollback_pointer_bytes = page_data[rollback_pointer_offset:rollback_pointer_offset+7]
            # 补充1个字节的0以满足8字节长度
            rollback_pointer_bytes = b'\x00' + rollback_pointer_bytes
            rollback_pointer_value = struct.unpack('>Q', rollback_pointer_bytes)[0]
            data_offset += 7

            # 解析变长字段
            name_len = var_lens[0]
            name_value = page_data[data_offset:data_offset+name_len].decode('utf8')
            data_offset += name_len

            # 解析age (1字节)
            age_value = page_data[data_offset] - 128
            data_offset += 1

            # 解析email
            email_len = var_lens[1]
            email_value = page_data[data_offset:data_offset+email_len].decode('utf8')
            data_offset += email_len + 1

            # 解析datetime (8字节)
            created_at_bytes = page_data[data_offset:data_offset+4]
            created_at_value = parse_datetime(
                struct.unpack('>I', created_at_bytes)[0]
            )

            # 返回解析后的记录
            return {
                'header': header,
                'null_flags': null_flags,
                'var_lens': var_lens,
                'trx_id': trx_id_value,
                'rollback_pointer': rollback_pointer_value,
                'data': {
                    'id': id_value,
                    'name': name_value,
                    'age': age_value,
                    'email': email_value,
                    'created_at': created_at_value
                }
            }
        except Exception as e:
            return {
                'header': header,
                'error': f"Failed to parse record data: {str(e)}"
            }

    def parse_page_directory(self, page_data: bytes, n_dir_slots: int) -> List[int]:
        """解析页目录(Page Directory)

        页目录是一个槽位数组，位于页面尾部。它的主要作用是加快记录的查找速度。
        每个槽位占用2个字节，按照大端序存储，指向一条记录在页面中的偏移量。

        工作原理:
        1. 页目录从页面尾部开始,向前增长
        2. 每个槽位2字节,存储记录的偏移量
        3. 槽位按照记录主键值升序排列
        4. 通过二分查找槽位可以快速定位到记录

        算法步骤:
        1. 计算页目录起始位置(页尾-8字节文件尾)
        2. 遍历n_dir_slots个槽位
        3. 每个槽位解析2字节偏移量
        4. 返回所有槽位值列表

        Args:
            page_data: 页面数据
            n_dir_slots: 槽位数量

        Returns:
            包含所有槽位值的列表
        """
        # 页目录从页面尾部开始，每个槽位2字节
        directory = []
        page_end = self.PAGE_SIZE - 8  # 减去File Trailer的8字节
        for i in range(n_dir_slots):
            slot_offset = page_end - (i + 1) * 2
            # 使用大端序('>H')读取槽位值
            slot = struct.unpack('>H', page_data[slot_offset:slot_offset+2])[0]
            directory.append(slot)
        return directory

    def analyze_records(self, page_data: bytes):
        """析页中的所有记录"""
        # 解析页头
        page_header = self.parse_page_header(page_data)
        if PageType(page_header['page_type']) != PageType.FIL_PAGE_INDEX:
            print("Not an index page")
            return

        # 解析索引头
        index_header = self.parse_index_header(page_data)

        # 获取页目录
        directory = self.parse_page_directory(page_data, index_header['n_dir_slots'])
        print(f"\npage directory: \n{directory}")
        print("\nRecords:")
        records = self.parse_records(page_data, directory)
        for record in records:
            print(json.dumps(record['data'], indent=4, ensure_ascii=False))

    def analyze_header(self):
        """分析整个文件"""
        print(f"Analyzing file: {self.file_path}")
        print(f"File size: {self.file_size:,} bytes")
        print(f"Total pages: {self.file_size // self.PAGE_SIZE:,}")

        with open(self.file_path, 'rb') as f:
            # 分析前三个页面
            for page_no in range(7):
                if page_no != 4:
                    continue
                f.seek(page_no * self.PAGE_SIZE)
                page_data = f.read(self.PAGE_SIZE)

                page_header = self.parse_page_header(page_data)
                try:
                    page_type = PageType(page_header['page_type'])
                except ValueError:
                    print(f"Warning: Unknown page type: {page_header['page_type']}")
                    page_type = PageType.FIL_PAGE_TYPE_ALLOCATED

                print(f"\nPage {page_no} (Type: {page_type.name}, Raw type: 0x{page_header['page_type']:x}):")
                self.print_page_header(page_header)

                # 如果是索引页，解析索引头部
                if page_type == PageType.FIL_PAGE_INDEX:
                    index_header = self.parse_index_header(page_data)
                    print("\nIndex Header:")
                    for key, value in index_header.items():
                        print(f"  {key}: {value}")
                    self.analyze_records(page_data)

                print("\nFirst 64 bytes of page:")
                self.hex_dump(page_data, page_no * self.PAGE_SIZE, 64)

def main():
    # 使用你的MySQL数据目录路径
    ibd_file = "/data/docker/mysql/data/storage_test/users.ibd"
    parser = IBDFileParser(ibd_file)
    parser.analyze_header()

if __name__ == "__main__":
    main()
