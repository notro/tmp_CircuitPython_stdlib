"""Recognize image file formats based on their first few bytes."""


#-------------------------#
# Recognize image headers #
#-------------------------#

def what(file, h=None):
    f = None
    try:
        if h is None:
            if isinstance(file, str):
                f = open(file, 'rb')
                h = f.read(32)
            else:
                location = file.tell()
                h = file.read(32)
                file.seek(location)
        for tf in tests:
            res = tf(h, f)
            if res:
                return res
    finally:
        if f: f.close()
    return None


#---------------------------------#
# Subroutines per image file type #
#---------------------------------#

tests = []

def test_jpeg(h, f):
    """JPEG data in JFIF or Exif format"""
    if h[6:10] in (b'JFIF', b'Exif'):
        return 'jpeg'

tests.append(test_jpeg)

def test_png(h, f):
    if h[:8] == b'\211PNG\r\n\032\n':                                           ###
        return 'png'

tests.append(test_png)

def test_gif(h, f):
    """GIF ('87 and '89 variants)"""
    if h[:6] in (b'GIF87a', b'GIF89a'):
        return 'gif'

tests.append(test_gif)

def test_tiff(h, f):
    """TIFF (can be in Motorola or Intel byte order)"""
    if h[:2] in (b'MM', b'II'):
        return 'tiff'

tests.append(test_tiff)

def test_rgb(h, f):
    """SGI image library"""
    if h[:2] == b'\001\332':                                                    ###
        return 'rgb'

tests.append(test_rgb)

def test_pbm(h, f):
    """PBM (portable bitmap)"""
    if len(h) >= 3 and \
        h[0] == ord(b'P') and h[1] in b'14' and h[2] in b' \t\n\r':
        return 'pbm'

tests.append(test_pbm)

def test_pgm(h, f):
    """PGM (portable graymap)"""
    if len(h) >= 3 and \
        h[0] == ord(b'P') and h[1] in b'25' and h[2] in b' \t\n\r':
        return 'pgm'

tests.append(test_pgm)

def test_ppm(h, f):
    """PPM (portable pixmap)"""
    if len(h) >= 3 and \
        h[0] == ord(b'P') and h[1] in b'36' and h[2] in b' \t\n\r':
        return 'ppm'

tests.append(test_ppm)

def test_rast(h, f):
    """Sun raster file"""
    if h[:4] == (b'\x59\xA6\x6A\x95'):                                          ###
        return 'rast'

tests.append(test_rast)

def test_xbm(h, f):
    """X bitmap (X10 or X11)"""
    if h[:8] == b'#define ':                                                    ###
        return 'xbm'

tests.append(test_xbm)

def test_bmp(h, f):
    if h[:2] == b'BM':                                                          ###
        return 'bmp'

tests.append(test_bmp)

