import re, sys, zlib, base64

def decode_stream(d):
    cand, s = [], d.strip()
    if s[:1] in (b'G', b'<') or s.endswith(b'~>'):
        try: cand.append(base64.a85decode(s, adobe=True))
        except Exception: pass
    cand.append(d)
    res = []
    for c in cand:
        res.append(c)
        for f in (zlib.decompress, lambda x: zlib.decompressobj().decompress(x)):
            try: res.append(f(c)); break
            except Exception: pass
    return res

def toks(data):
    r = []
    for tm in re.finditer(rb'\((?:\\.|[^\\()])*\)|TD|Td|T\*|TJ|Tj|ET', data, re.S):
        t = tm.group(0)
        if t in (b'TD', b'Td', b'T*', b'ET'):
            r.append('\n')
        elif t.startswith(b'('):
            s = t[1:-1]
            s = re.sub(rb'\\([0-7]{1,3})', lambda x: bytes([int(x.group(1), 8) & 0xFF]), s)
            s = re.sub(rb'\\([()\\])', rb'\1', s)
            s = s.replace(b'\\n', b'\n').replace(b'\\r', b'').replace(b'\\t', b' ')
            s = s.replace(b'\x00', b'')
            r.append(s.decode('latin-1'))
    return ''.join(r)

WORDS = re.compile(r'\b(the|and|for|with|com|linkedin|https|www|director|producer|agency|'
                   r'marketing|creative|de|la|en|rol|lead|email|https)\b', re.I)
def score(t):
    if not t.strip(): return -1
    printable = sum(c.isalnum() or c in " \n.,:/@&-_()'#!?" for c in t) / len(t)
    return printable + 0.5 * min(len(WORDS.findall(t)) / max(len(t) / 60, 1), 2)

def best_shift(t):
    b, bk = score(t), 0
    for k in range(1, 64):
        c = ''.join(chr((ord(x) + k) % 256) if x != '\n' else x for x in t)
        s = score(c)
        if s > b: b, bk = s, k
    return bk

def extract(path):
    raw = open(path, 'rb').read()
    chunks = []
    for m in re.finditer(rb'stream\r?\n(.*?)\r?\n?endstream', raw, re.S):
        for d in decode_stream(m.group(1)):
            if b'Tj' in d or b'TJ' in d:
                t = toks(d)
                k = best_shift(t)                     # offset POR STREAM
                if k: t = ''.join(chr((ord(x)+k) % 256) if x != '\n' else x for x in t)
                chunks.append(t)
                break
    return re.sub(r'\n{3,}', '\n\n', '\n'.join(chunks))

if __name__ == '__main__':
    print(extract(sys.argv[1]))

# Uso: python3 pdf_extract.py archivo.pdf > salida.txt
#
# Extractor de texto de PDF sin dependencias (poppler/pypdf no estan disponibles en
# el contenedor). Maneja: ASCII85 + FlateDecode (ReportLab), streams sin comprimir,
# texto guardado en 2 bytes, y fuentes subseteadas con offset de codigo por stream.
# Sirve tambien para el SL-26 Sales Intelligence PDF que menciona el BRIEF.
