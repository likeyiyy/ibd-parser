def parse_datetime(value: int) -> str:
    second = value & 0x3F
    value = value >> 6

    minute = value & 0x3F
    value = value >> 6

    hour = value & 0x1F
    value = value >> 5

    day = value & 0x1F
    value = value >> 5

    month = (value % 13 + 3) % 13
    if value % 13 >= 11:
        year = value // 13 + DATETIME_EPOCH_YEAR
    else:
        year = value // 13 + DATETIME_EPOCH_YEAR - 1

    return f"{year:04d}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:02d}"

def hex_dump(data: bytes, start: int = 0, length: int = 64) -> None:
    for i in range(0, min(length, len(data)), 16):
        print(f'{start+i:04x}: ', end='')
        hex_data = ' '.join(f'{b:02x}' for b in data[i:i+16])
        print(f'{hex_data:<48}', end='  ')
        ascii_data = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in data[i:i+16])
        print(ascii_data)
