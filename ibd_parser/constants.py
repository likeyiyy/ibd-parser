from enum import IntEnum

PAGE_SIZE = 16384
FIL_PAGE_OFFSET = 38
FIL_PAGE_DATA = 38
DATETIME_EPOCH_YEAR = 1970

class PageType(IntEnum):
    FIL_PAGE_TYPE_ALLOCATED = 0
    FIL_PAGE_TYPE_UNDO_LOG = 2
    FIL_PAGE_TYPE_INODE = 3
    FIL_PAGE_TYPE_IBUF_FREE_LIST = 4
    FIL_PAGE_TYPE_IBUF_BITMAP = 5
    FIL_PAGE_TYPE_SYS = 6
    FIL_PAGE_TYPE_TRX_SYS = 7
    FIL_PAGE_TYPE_FSP_HDR = 8
    FIL_PAGE_TYPE_XDES = 9
    FIL_PAGE_TYPE_BLOB = 10
    FIL_PAGE_SDI = 17853
    FIL_PAGE_RTREE = 17854
    FIL_PAGE_INDEX = 17855

    @classmethod
    def _missing_(cls, value):
        swapped = ((value & 0xFF) << 8) | ((value & 0xFF00) >> 8)
        if swapped in cls._value2member_map_:
            return cls._value2member_map_[swapped]
        print(f"Warning: Unknown page type: {swapped} (0x{swapped:x})")
        return cls.FIL_PAGE_TYPE_ALLOCATED

class RecordType(IntEnum):
    CONVENTIONAL = 0
    INFIMUM = 1
    SUPREMUM = 2
