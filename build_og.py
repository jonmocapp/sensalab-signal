# -*- coding: utf-8 -*-
"""Generate a real on-brand og.jpg (1200x630) via HTML+Edge screenshot, plus favicons from the isotipo."""
import base64, pathlib
from io import BytesIO
from PIL import Image
BLOG = pathlib.Path(r"C:\Dev\SensaLab-Newsletter-Bot\blog")
FDIR = pathlib.Path(r"C:\Users\jonmo\OneDrive\Desktop\SensaLab\02-Marca\KMR Apparat\KMR Apparat\WEB\WOFF2")
MED  = pathlib.Path(r"C:\Users\jonmo\OneDrive\Desktop\SensaLab\06-Web-y-Dev\Newsletter\ediciones\2026-08-Signal\substack")
def b64(p): return base64.b64encode(pathlib.Path(p).read_bytes()).decode()

FONT = "".join(
 "@font-face{font-family:'Apparat';font-weight:%d;src:url(data:font/woff2;base64,%s) format('woff2')}" % (w, b64(FDIR/f))
 for w,f in [(700,"KMR-Apparat-Bold.woff2"),(900,"KMR-Apparat-Black.woff2")])
ISO = "data:image/png;base64," + b64(MED/"isotipo.png")

OG = ("<!doctype html><html><head><meta charset='utf-8'><style>"
 + FONT +
 "*{margin:0;box-sizing:border-box}html,body{width:1200px;height:630px;overflow:hidden}"
 "body{font-family:'Apparat',Arial,sans-serif;background:#EEF1FB;position:relative}"
 ".b1{position:absolute;width:560px;height:560px;border-radius:50%;filter:blur(70px);opacity:.55;left:-120px;top:-160px;background:radial-gradient(circle,#32BFFC,transparent 62%)}"
 ".b2{position:absolute;width:520px;height:520px;border-radius:50%;filter:blur(70px);opacity:.5;right:-120px;bottom:-180px;background:radial-gradient(circle,#B55CB7,transparent 62%)}"
 ".b3{position:absolute;width:480px;height:480px;border-radius:50%;filter:blur(70px);opacity:.4;right:180px;top:-160px;background:radial-gradient(circle,#6060BE,transparent 62%)}"
 ".in{position:relative;z-index:2;padding:76px 84px;height:100%;display:flex;flex-direction:column;justify-content:space-between}"
 ".top{display:flex;align-items:center;gap:14px}.top img{height:44px}.top b{font-weight:900;font-size:30px;color:#1C1956;letter-spacing:-.01em}"
 ".mid h1{font-weight:900;font-size:92px;line-height:.98;letter-spacing:-.035em;color:#1C1956;max-width:20ch}"
 ".grad{background:linear-gradient(90deg,#32BFFC,#3D76E8,#6060BE,#B55CB7);-webkit-background-clip:text;background-clip:text;color:transparent}"
 ".mid p{margin-top:22px;font-weight:700;font-size:30px;color:#787878;max-width:30ch}"
 ".bot{font-weight:700;font-size:22px;color:#1C1956;opacity:.8}"
 "</style></head><body><div class='b1'></div><div class='b2'></div><div class='b3'></div>"
 "<div class='in'><div class='top'><img src='" + ISO + "'><b>The Signal</b></div>"
 "<div class='mid'><h1>Immersive and experiential <span class='grad'>signals</span> worth your week.</h1>"
 "<p>Real moves in experiential marketing, every two weeks.</p></div>"
 "<div class='bot'>by SensaLab &middot; Los Angeles</div></div></body></html>")
(BLOG/"_og.html").write_text(OG, encoding="utf-8")
print("wrote _og.html")

# favicons from isotipo
iso = Image.open(MED/"isotipo.png").convert("RGBA")
for size, name in [(32,"favicon-32.png"),(180,"apple-touch-icon.png"),(192,"icon-192.png")]:
    im = iso.copy(); im.thumbnail((size,size), Image.LANCZOS)
    canvas = Image.new("RGBA",(size,size),(0,0,0,0))
    canvas.paste(im, ((size-im.width)//2,(size-im.height)//2), im)
    canvas.save(BLOG/name)
    print("wrote", name)
