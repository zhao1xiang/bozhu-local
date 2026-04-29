import struct

def get_jpeg_size(path):
    with open(path, 'rb') as f:
        f.read(2)  # SOI marker FF D8
        while True:
            marker = f.read(2)
            if len(marker) < 2:
                break
            if marker[0] != 0xFF:
                break
            # SOF markers: C0-C3, C5-C7, C9-CB, CD-CF
            if marker[1] in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
                f.read(3)  # length(2) + precision(1)
                h = struct.unpack('>H', f.read(2))[0]
                w = struct.unpack('>H', f.read(2))[0]
                return w, h
            else:
                length = struct.unpack('>H', f.read(2))[0]
                f.read(length - 2)
    return None, None

w, h = get_jpeg_size('frontend/public/print-template.png')
print(f"宽: {w}px  高: {h}px")
if w and h:
    print(f"宽高比: {h/w:.4f}")
