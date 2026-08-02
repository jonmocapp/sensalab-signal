# -*- coding: utf-8 -*-
"""
The Signal, email pipeline.
Turns the LIGHT web edition (the b1/Pearl design Jon loves) into a self contained
Gmail email by rendering it as retina image strips. This is THE approved way to get
the design into the inbox (email HTML cannot render the real design).

Usage:
    python signal_email_pipeline.py <path-to-light-edition.html> [issue_no]

Output: writes Signal-<issue>-EMAIL-claro.html into the SensaLab email folder, with
the strips hosted, and prints the strip URLs. Then create the Gmail draft from that
HTML (that step uses the Gmail connector, done by the assistant).
"""
import sys, subprocess, tempfile, pathlib
from PIL import Image

MSEDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
OUTDIR = pathlib.Path(r"C:\Users\jonmo\OneDrive\Desktop\SensaLab\06-Web-y-Dev\Newsletter\ediciones\2026-08-Signal\email")
DEFAULT_SRC = r"C:\Users\jonmo\OneDrive\Desktop\SensaLab\06-Web-y-Dev\Newsletter\ediciones\2026-08-Signal\web\Signal-20-hoy-web.html"


def render(src_html, out_png):
    prof = tempfile.mkdtemp()
    subprocess.run([MSEDGE, "--headless=new", "--no-sandbox", "--no-first-run",
        "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=2",
        "--window-size=600,5600", "--virtual-time-budget=6000",
        "--user-data-dir=" + prof, "--screenshot=" + str(out_png),
        pathlib.Path(src_html).as_uri()], check=False)


def trim_and_slice(png, n=6):
    im = Image.open(png).convert("RGB"); W, H = im.size; px = im.load()
    trail = px[W // 2, H - 1]
    def rowdiff(y):
        return max(max(abs(px[x, y][c] - trail[c]) for c in range(3)) for x in range(0, W, 60))
    bottom = H
    for y in range(H - 1, 0, -3):
        if rowdiff(y) > 18:
            bottom = min(H, y + 24); break
    im = im.crop((0, 0, W, bottom)); W, H2 = im.size
    step = -(-H2 // n); out = []
    for i in range(n):
        y0 = i * step; y1 = min(H2, (i + 1) * step)
        if y0 >= y1: break
        s = im.crop((0, y0, W, y1)); p = png.parent / ("strip%d.jpg" % (i + 1))
        s.save(p, quality=87, optimize=True); out.append(p)
    return out


def upload(p):
    r = subprocess.run(["curl", "-s", "-A", "Mozilla/5.0", "-F", "reqtype=fileupload",
        "-F", "fileToUpload=@" + str(p), "https://catbox.moe/user/api.php"],
        capture_output=True, text=True)
    return r.stdout.strip()


def build_email(urls, issue):
    rows = ""
    for i, u in enumerate(urls):
        alt = ("The Signal, edition " + issue) if i == 0 else ""
        rows += ('<tr><td style="padding:0;font-size:0;line-height:0;"><img src="%s" width="600" alt="%s" '
                 'style="width:100%%;max-width:600px;height:auto;display:block;border:0;"></td></tr>' % (u, alt))
    return ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
      '<meta name="viewport" content="width=device-width,initial-scale=1">'
      '<meta name="color-scheme" content="light only"><title>The Signal</title></head>'
      '<body style="margin:0;padding:0;background:#E8F1FA;">'
      '<table role="presentation" width="100%" cellpadding="0" cellspacing="0" bgcolor="#E8F1FA" style="background:#E8F1FA;">'
      '<tr><td align="center" style="padding:0;">'
      '<table role="presentation" width="600" cellpadding="0" cellspacing="0" style="width:600px;max-width:600px;">'
      + rows +
      '<tr><td bgcolor="#0B0F0F" style="background:#0B0F0F;padding:30px 34px 34px;" align="center">'
      '<table role="presentation" cellpadding="0" cellspacing="0" align="center"><tr>'
      '<td bgcolor="#F4F3F3" style="background:#F4F3F3;border-radius:999px;">'
      '<a href="mailto:hello@sensalab.io" style="display:inline-block;color:#1C1956;text-decoration:none;padding:14px 32px;font:800 14px/1 \'Helvetica Neue\',Arial,sans-serif;">Reply to talk &#8594;</a>'
      '</td></tr></table>'
      '<p style="margin:18px 0 0;font:400 11px/1.6 \'Helvetica Neue\',Arial,sans-serif;color:#787878;">&#169; 2026 SensaLab, Inc. &middot; Los Angeles, CA, USA &middot; '
      '<a href="mailto:hello@sensalab.io" style="color:#E4E4EF;text-decoration:underline;">hello@sensalab.io</a></p>'
      '</td></tr></table></td></tr></table></body></html>')


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_SRC
    issue = sys.argv[2] if len(sys.argv) > 2 else "20"
    work = pathlib.Path(tempfile.mkdtemp()); png = work / "full.png"
    print("rendering", src); render(src, png)
    print("slicing"); strips = trim_and_slice(png)
    print("uploading"); urls = [upload(p) for p in strips]
    for u in urls: print("  ", u)
    OUTDIR.mkdir(parents=True, exist_ok=True)
    outp = OUTDIR / ("Signal-%s-EMAIL-claro.html" % issue)
    outp.write_text(build_email(urls, issue), encoding="utf-8")
    print("email HTML ->", outp)


if __name__ == "__main__":
    main()
