# -*- coding: utf-8 -*-
"""The Signal home (direction B): LIGHT + liquid glass, hero carousel, filterable news grid,
free-kit lead magnet with email capture, real (Netlify) forms, hamburger nav, hardened carousel,
accessibility, SEO/GEO. Opus build."""
import html
from signal_content import (BLOG, FONT, ISO, STORIES, FILTERS, CAROUSEL, KITS, FAQ, ARCH, DATE,
 SERVICES, HOWWEWORK, RESULTS)
try:
    from signals_feed import SIGNALS   # Carril 1: feed diario de noticias reales (links a la fuente)
except Exception:
    SIGNALS = []

def art(slug): return "article-%s.html" % slug

CSS = r"""
*{margin:0;padding:0;box-sizing:border-box}
:root{--ink:#1C1956;--body:#0B0F0F;--paper:#F4F3F3;--lav:#E4E4EF;--mut:#787878;--glass:rgba(255,255,255,.58);--gline:rgba(255,255,255,.7)}
html{scroll-behavior:smooth}
body{font-family:'Apparat','Helvetica Neue',Arial,sans-serif;color:var(--body);background:#EEF1FB;-webkit-font-smoothing:antialiased;overflow-x:hidden}
a{color:inherit;text-decoration:none}
img{display:block;max-width:100%}
:focus-visible{outline:3px solid #3D76E8;outline-offset:2px;border-radius:8px}
.skip{position:absolute;left:-9999px;top:8px;z-index:1000;background:#1C1956;color:#F4F3F3;padding:10px 16px;border-radius:999px;font-weight:800;font-size:13px}
.skip:focus{left:16px}
.wrap{max-width:1160px;margin:0 auto;padding-left:clamp(20px,4vw,44px);padding-right:clamp(20px,4vw,44px)}
[id]{scroll-margin-top:96px}
.bg{position:fixed;inset:0;overflow:hidden;z-index:0;pointer-events:none}
#motes{position:fixed;inset:0;z-index:0;pointer-events:none}
.blob{position:absolute;border-radius:50%;filter:blur(70px);opacity:.5;pointer-events:none;will-change:transform;animation:blobDrift 90s ease-in-out infinite alternate}
.b1{width:52vw;height:52vw;left:-14vw;top:-16vw;background:radial-gradient(circle,#32BFFC,transparent 62%)}
.b2{width:46vw;height:46vw;right:-12vw;top:-6vw;background:radial-gradient(circle,#B55CB7,transparent 62%);animation-duration:115s;animation-delay:-40s}
.b3{width:50vw;height:50vw;left:22vw;bottom:-24vw;background:radial-gradient(circle,#6060BE,transparent 62%);animation-duration:140s;animation-delay:-70s}
@keyframes blobDrift{from{transform:translate(0,0) scale(1) rotate(0deg)}to{transform:translate(2.5%,-3%) scale(1.06) rotate(6deg)}}
main,header,footer,.prog{position:relative;z-index:1}
.prog{position:fixed;top:0;left:0;height:3px;width:0;z-index:60;background:linear-gradient(90deg,#32BFFC,#3D76E8,#6060BE,#B55CB7)}
/* nav */
.nav{position:sticky;top:0;z-index:50;transition:all .3s;padding:0 clamp(12px,4vw,22px)}
.nav .in{margin:12px auto;max-width:1160px;padding:12px clamp(16px,3vw,24px);display:flex;align-items:center;justify-content:space-between;
  background:var(--glass);backdrop-filter:saturate(1.5) blur(20px);-webkit-backdrop-filter:saturate(1.5) blur(20px);
  border:1px solid var(--gline);border-radius:999px;box-shadow:0 10px 34px rgba(28,25,86,.10)}
.nav.scrolled .in{box-shadow:0 14px 40px rgba(28,25,86,.16);background:rgba(255,255,255,.72)}
.brand{display:flex;align-items:center;gap:9px}
.brand img{height:26px}
.brand b{font-weight:800;font-size:19px;letter-spacing:-.01em;color:var(--ink)}
.nlinks{display:flex;gap:24px}
.nlinks a{font-weight:700;font-size:14px;color:var(--ink);opacity:.7;transition:opacity .2s}
.nlinks a:hover{opacity:1}
.nav .cta{display:flex;gap:10px;align-items:center}
.ghost{font-weight:700;font-size:13px;color:var(--ink);padding:10px 16px;border-radius:999px;border:1px solid rgba(28,25,86,.18);transition:background .2s}
.ghost:hover{background:rgba(28,25,86,.06)}
.solid{font-weight:800;font-size:13px;color:#F4F3F3;padding:11px 20px;border-radius:999px;background:linear-gradient(90deg,#3D76E8,#6060BE 55%,#B55CB7);box-shadow:0 8px 22px rgba(96,96,190,.35);transition:transform .2s}
.solid:hover{transform:translateY(-2px)}
.navtoggle{display:none;background:none;border:0;cursor:pointer;width:40px;height:40px;border-radius:12px;color:var(--ink)}
.navtoggle svg{width:22px;height:22px}
.mobmenu{display:none;max-width:1160px;margin:0 auto;padding:10px clamp(16px,3vw,24px)}
.mobmenu.open{display:block}
.mobmenu .panel{background:rgba(255,255,255,.86);backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);border:1px solid var(--gline);border-radius:22px;padding:16px;box-shadow:0 16px 40px rgba(28,25,86,.16);display:flex;flex-direction:column;gap:4px}
.mobmenu a{padding:12px 14px;border-radius:12px;font-weight:700;font-size:15px;color:var(--ink)}
.mobmenu a:hover{background:rgba(28,25,86,.06)}
.mobmenu a.solid{color:#F4F3F3;text-align:center;margin-top:6px}
@media(max-width:820px){.nlinks{display:none}.nav .cta{display:none}.navtoggle{display:grid;place-items:center}}
/* section rhythm (longhand so .wrap horizontal padding can't cancel it) */
section{padding-top:clamp(58px,6.5vw,94px);padding-bottom:clamp(58px,6.5vw,94px)}
.hire,.subs{scroll-margin-top:96px}
.eyebrow{display:inline-flex;align-items:center;gap:10px;font-weight:800;font-size:12px;letter-spacing:.14em;color:var(--ink);opacity:.7;margin-bottom:16px}
.eyebrow i{width:8px;height:8px;border-radius:50%;background:linear-gradient(135deg,#32BFFC,#B55CB7)}
.lede{font-weight:900;font-size:clamp(26px,3.1vw,40px);line-height:1.12;letter-spacing:-.025em;color:var(--ink);max-width:20ch}
.dek{margin-top:16px;font-weight:500;font-size:clamp(15px,1.5vw,18px);line-height:1.6;color:var(--mut);max-width:62ch}
.dek b{color:var(--ink);font-weight:700}
/* hero carousel */
.hero{margin-top:26px}
.carousel{position:relative;border-radius:26px;overflow:hidden;box-shadow:0 30px 80px rgba(28,25,86,.20)}
.track{position:relative;height:clamp(360px,50vw,540px)}
.slide{position:absolute;inset:0;opacity:0;transform:translateX(42px) scale(1.015);transition:opacity .5s ease,transform .6s cubic-bezier(.22,1,.36,1);pointer-events:none}
.slide.on{opacity:1;transform:none;pointer-events:auto}
.cring{position:absolute;top:18px;right:126px;z-index:5;width:34px;height:34px;transform:rotate(-90deg);pointer-events:none}
.cring circle{fill:none;stroke-width:3}
.cring .bg{stroke:rgba(255,255,255,.4)}
.cring .fill{stroke:#F4F3F3;stroke-linecap:round;stroke-dasharray:88;stroke-dashoffset:88}
.cring .fill.run{animation:cfill 4s linear forwards}
@keyframes cfill{to{stroke-dashoffset:0}}
@media(max-width:560px){.cring{display:none}}
.slide img{width:100%;height:100%;object-fit:cover;transform:scale(1.07);transition:transform 7s ease-out}
.slide.on img{transform:scale(1)}
.fscrim{position:absolute;inset:0;background:linear-gradient(180deg,rgba(11,15,15,0) 38%,rgba(11,15,15,.5) 74%,rgba(11,15,15,.84) 100%)}
.fcard{position:absolute;left:clamp(18px,3vw,34px);bottom:clamp(18px,3vw,32px);right:clamp(18px,3vw,34px);
  background:rgba(20,19,52,.30);backdrop-filter:blur(14px);-webkit-backdrop-filter:blur(14px);border:1px solid rgba(255,255,255,.22);border-radius:20px;padding:clamp(18px,2.2vw,26px);color:#F4F3F3;max-width:600px}
.fchip{display:inline-block;font-weight:800;font-size:11px;letter-spacing:.06em;background:linear-gradient(90deg,#3D76E8,#B55CB7);padding:6px 12px;border-radius:999px;margin-bottom:12px}
.fcard .fh{font-weight:900;font-size:clamp(22px,2.7vw,34px);line-height:1.08;letter-spacing:-.025em;text-shadow:0 4px 26px rgba(0,0,0,.4)}
.fcard p{margin-top:10px;font-weight:500;font-size:clamp(13px,1.3vw,15px);line-height:1.5;color:#E4E4EF;max-width:52ch}
.fcard .go{display:inline-block;margin-top:16px;background:#F4F3F3;color:#1C1956;font-weight:800;font-size:14px;padding:12px 24px;border-radius:999px;transition:transform .2s}
.fcard .go:hover{transform:translateY(-2px)}
.cap{position:absolute;top:16px;left:16px;background:rgba(20,19,52,.32);backdrop-filter:blur(10px);border:1px solid rgba(255,255,255,.2);color:#F4F3F3;font-weight:700;font-size:11px;letter-spacing:.04em;padding:8px 14px;border-radius:999px}
.cbtn{position:absolute;top:18px;z-index:5;width:42px;height:42px;border-radius:50%;background:rgba(255,255,255,.85);backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px);border:1px solid var(--gline);display:grid;place-items:center;cursor:pointer;color:var(--ink);font:800 20px/1 Arial;transition:transform .2s}
.cbtn:hover{transform:scale(1.08)}
.cprev{right:70px}.cnext{right:18px}
.cdots{display:flex;gap:8px;justify-content:center;margin-top:18px}
.cdot{width:9px;height:9px;border-radius:50%;background:rgba(28,25,86,.22);cursor:pointer;transition:all .3s;border:0;padding:0}
.cdot.on{width:28px;border-radius:6px;background:linear-gradient(90deg,#3D76E8,#B55CB7)}
@media(max-width:560px){.cbtn{width:40px;height:40px;font-size:18px}}
/* section head */
.shead{display:flex;align-items:baseline;justify-content:space-between;gap:16px;margin-bottom:26px}
.shead h2{font-weight:900;font-size:clamp(25px,3vw,38px);letter-spacing:-.02em;color:var(--ink)}
.shead .m{font-weight:700;font-size:13px;letter-spacing:.06em;color:var(--mut);white-space:nowrap}
/* filters */
.filters{display:flex;flex-wrap:wrap;gap:10px;margin-bottom:28px}
.fpill{font:700 13px/1 'Apparat',Arial,sans-serif;color:var(--ink);background:var(--glass);border:1px solid var(--gline);border-radius:999px;padding:11px 18px;cursor:pointer;transition:transform .18s,box-shadow .18s,background .18s;backdrop-filter:blur(10px);-webkit-backdrop-filter:blur(10px)}
.fpill:hover{transform:translateY(-1px);box-shadow:0 8px 20px rgba(28,25,86,.12)}
.fpill.on{color:#F4F3F3;background:linear-gradient(90deg,#3D76E8,#6060BE 55%,#B55CB7);border-color:transparent;box-shadow:0 8px 22px rgba(96,96,190,.34)}
/* cards grid */
.g3{display:grid;grid-template-columns:repeat(3,1fr);gap:24px}
@media(max-width:900px){.g3{grid-template-columns:1fr 1fr}}
@media(max-width:620px){.g3{grid-template-columns:1fr}}
.card{display:flex;flex-direction:column;background:var(--glass);backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px);border:1px solid var(--gline);border-radius:22px;overflow:hidden;box-shadow:0 16px 44px rgba(28,25,86,.10);transition:transform .3s,box-shadow .3s}
.card:hover{transform:translateY(-6px);box-shadow:0 30px 70px rgba(28,25,86,.18)}
.card.hide{display:none}
.phwrap{overflow:hidden;display:block}
.card .ph{height:190px;background-size:cover;background-position:center;transition:transform .5s ease}
.card:hover .ph{transform:scale(1.05)}
.card .cin{padding:20px 22px 20px;display:flex;flex-direction:column;flex:1}
.chip{align-self:flex-start;font-weight:800;font-size:11px;letter-spacing:.05em;color:var(--ink);background:rgba(28,25,86,.08);border-radius:999px;padding:6px 12px;margin-bottom:12px}
.card h3{font-weight:900;font-size:19px;line-height:1.18;letter-spacing:-.01em;color:var(--ink)}
.card .sum{margin-top:9px;font-weight:500;font-size:14px;line-height:1.55;color:var(--body)}
.cmeta{margin-top:auto;display:flex;align-items:center;justify-content:space-between;gap:12px;padding-top:16px;border-top:1px solid rgba(28,25,86,.09)}
.cmeta .dt{font-weight:700;font-size:12px;color:var(--mut)}
.cmeta .rd{font-weight:800;font-size:13px;color:var(--ink)}
.cmeta .rd:hover{opacity:.7}
#grid{transition:opacity .2s ease}
/* free kit */
.kits{display:grid;grid-template-columns:repeat(4,1fr);gap:20px}
@media(max-width:900px){.kits{grid-template-columns:1fr 1fr}}
@media(max-width:560px){.kits{grid-template-columns:1fr}}
.kit{position:relative;overflow:hidden;text-align:left;cursor:pointer;border:0;border-radius:22px;padding:26px 24px 22px;display:flex;flex-direction:column;gap:5px;color:#F4F3F3;min-height:216px;transition:transform .25s,box-shadow .25s;font-family:'Apparat',Arial,sans-serif;box-shadow:0 16px 40px rgba(28,25,86,.16)}
.kit:hover{transform:translateY(-6px);box-shadow:0 30px 64px rgba(28,25,86,.30)}
.kit>span{position:relative;z-index:1}
.kit::after{content:'';position:absolute;inset:0;border-radius:inherit;background:linear-gradient(115deg,transparent 36%,rgba(255,255,255,.42) 50%,transparent 64%);transform:translateX(-130%);pointer-events:none;animation:shimmer 7s ease-in-out infinite}
.k1::after{animation-delay:0s}.k2::after{animation-delay:1.4s}.k3::after{animation-delay:2.8s}.k4::after{animation-delay:4.2s}
@keyframes shimmer{0%,55%{transform:translateX(-130%)}78%,100%{transform:translateX(130%)}}
.card.reveal-new{animation:cardIn .55s cubic-bezier(.16,1,.3,1) both}
@keyframes cardIn{from{opacity:0;transform:translateY(22px)}to{opacity:1;transform:none}}
.k1{background:linear-gradient(150deg,#32BFFC,#3D76E8)}
.k2{background:linear-gradient(150deg,#3D76E8,#6060BE)}
.k3{background:linear-gradient(150deg,#6060BE,#B55CB7)}
.k4{background:linear-gradient(150deg,#1C1956,#6060BE)}
.kit .kn{font-weight:900;font-size:56px;line-height:.85;letter-spacing:-.03em}
.kit .kt{font-weight:800;font-size:19px;letter-spacing:-.01em;margin-top:4px}
.kit .kd{font-weight:500;font-size:13px;line-height:1.45;color:#E4E4EF}
.kit .kgo{margin-top:auto;font-weight:800;font-size:13px;padding-top:14px}
/* hire */
.hire{border-radius:30px;overflow:hidden;position:relative;color:#F4F3F3;background:linear-gradient(120deg,#1C1956,#3D76E8 52%,#6060BE)}
.hire .hin{position:relative;padding:clamp(46px,6vw,78px) clamp(26px,5vw,64px);text-align:center}
.hire h2{font-weight:900;font-size:clamp(28px,4vw,50px);letter-spacing:-.025em;max-width:18ch;margin:0 auto}
.hire p{margin:16px auto 28px;font-weight:500;font-size:clamp(16px,1.6vw,18px);color:#E4E4EF;max-width:52ch;line-height:1.55}
.hire .row{display:flex;gap:12px;justify-content:center;flex-wrap:wrap}
.hire .p1{background:#F4F3F3;color:#1C1956;font-weight:800;font-size:16px;padding:16px 34px;border-radius:999px;transition:transform .2s}
.hire .p2{border:1px solid rgba(255,255,255,.4);color:#F4F3F3;font-weight:800;font-size:16px;padding:16px 30px;border-radius:999px;transition:background .2s}
.hire .p2:hover{background:rgba(255,255,255,.12)}
.hire .p1:hover{transform:translateY(-2px)}
/* faq */
.faqwrap{display:grid;grid-template-columns:330px 1fr;gap:clamp(30px,4vw,60px);align-items:start}
@media(max-width:860px){.faqwrap{grid-template-columns:1fr;gap:24px}}
.faqside{position:sticky;top:108px}
@media(max-width:860px){.faqside{position:static}}
.faqside h2{font-weight:900;font-size:clamp(25px,3vw,36px);letter-spacing:-.02em;color:var(--ink);margin-top:4px}
.faqside p{margin-top:14px;font-weight:500;font-size:16px;line-height:1.6;color:var(--mut);max-width:34ch}
.faqcta{display:inline-block;margin-top:20px;font-weight:800;font-size:14px;color:var(--ink);border-bottom:2px solid rgba(28,25,86,.25);padding-bottom:3px;transition:border-color .2s}
.faqcta:hover{border-color:var(--ink)}
.faq{display:grid;gap:14px}
.qa{background:var(--glass);backdrop-filter:blur(14px);-webkit-backdrop-filter:blur(14px);border:1px solid var(--gline);border-radius:16px;overflow:hidden;transition:box-shadow .2s}
.qa.open{box-shadow:0 14px 36px rgba(28,25,86,.12)}
.qa button{width:100%;text-align:left;background:none;border:0;cursor:pointer;padding:20px 22px;display:flex;justify-content:space-between;align-items:center;gap:16px;font:800 17px/1.3 'Apparat',Arial,sans-serif;color:var(--ink)}
.qa .plus{flex:none;width:24px;height:24px;border-radius:50%;background:linear-gradient(135deg,#3D76E8,#B55CB7);color:#F4F3F3;display:grid;place-items:center;font-weight:800;transition:transform .3s}
.qa.open .plus{transform:rotate(45deg)}
.qa .ans{max-height:0;overflow:hidden;transition:max-height .35s ease}
.qa .ans p{padding:0 22px 20px;font-weight:500;font-size:15px;line-height:1.6;color:var(--body)}
/* subscribe */
.subs{border-radius:26px;background:var(--glass);backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px);border:1px solid var(--gline);box-shadow:0 18px 50px rgba(28,25,86,.10);padding:clamp(40px,5vw,66px);text-align:center}
.subs h2{font-weight:900;font-size:clamp(25px,3.2vw,40px);letter-spacing:-.02em;color:var(--ink);max-width:18ch;margin:0 auto}
.subs .sp{margin:14px auto 24px;font-weight:500;font-size:16px;line-height:1.55;color:var(--mut);max-width:48ch}
.form{display:flex;gap:10px;justify-content:center;max-width:470px;margin:0 auto;flex-wrap:wrap}
.form input[type=email]{flex:1;min-width:210px;border:1px solid rgba(28,25,86,.16);border-radius:999px;padding:15px 22px;font:500 15px 'Apparat',Arial,sans-serif;background:rgba(255,255,255,.7);outline:none;transition:border-color .2s,box-shadow .2s}
.form input[type=email]:focus{border-color:#6060BE;box-shadow:0 0 0 4px rgba(96,96,190,.16)}
.form button{border:0;border-radius:999px;padding:15px 30px;font-weight:800;font-size:15px;color:#F4F3F3;background:linear-gradient(90deg,#3D76E8,#6060BE 55%,#B55CB7);cursor:pointer;transition:transform .2s}
.form button:hover{transform:translateY(-2px)}
.hp{position:absolute;left:-5000px}
.okmsg{display:none;font-weight:800;font-size:17px;color:var(--ink);padding:10px 0}
.reassure{margin:15px auto 0;font-weight:600;font-size:13px;letter-spacing:.02em;color:var(--mut)}
.trust{margin:22px auto 0;font-weight:700;font-size:13px;color:var(--ink);opacity:.72}
/* modal */
.modal{position:fixed;inset:0;z-index:200;background:rgba(20,19,52,.5);backdrop-filter:blur(6px);-webkit-backdrop-filter:blur(6px);display:none;align-items:center;justify-content:center;padding:22px}
.modal.show{display:flex}
.mbox{position:relative;max-width:470px;width:100%;background:#F7F7FC;border:1px solid var(--gline);border-radius:24px;padding:clamp(30px,4vw,42px);box-shadow:0 40px 100px rgba(28,25,86,.4)}
.mclose{position:absolute;top:14px;right:18px;border:0;background:none;font:800 26px/1 Arial;color:var(--mut);cursor:pointer}
.mbox h3{font-weight:900;font-size:clamp(22px,3vw,30px);color:var(--ink);letter-spacing:-.02em;margin-top:2px}
.mbox .mp{margin:12px 0 20px;font-weight:500;font-size:15px;line-height:1.55;color:var(--mut)}
.mform{display:flex;gap:10px;flex-wrap:wrap}
.mform input[type=email]{flex:1;min-width:180px;border:1px solid rgba(28,25,86,.16);border-radius:999px;padding:14px 20px;font:500 15px 'Apparat',Arial,sans-serif;background:#fff;outline:none}
.mform input[type=email]:focus{border-color:#6060BE;box-shadow:0 0 0 4px rgba(96,96,190,.16)}
.mform button{border:0;border-radius:999px;padding:14px 26px;font-weight:800;font-size:15px;color:#F4F3F3;background:linear-gradient(90deg,#3D76E8,#6060BE 55%,#B55CB7);cursor:pointer}
.mthanks{display:none}
.mthanks p{font-weight:700;font-size:16px;line-height:1.5;color:var(--ink);margin-bottom:16px}
.mthanks a{display:inline-block;font-weight:800;font-size:15px;color:#F4F3F3;background:linear-gradient(90deg,#3D76E8,#6060BE 55%,#B55CB7);padding:13px 24px;border-radius:999px}
/* footer */
.foot{padding:44px 0 64px;color:var(--mut);font-size:13px;line-height:1.9}
.foot b{color:var(--ink);font-weight:800;font-size:16px}
.foot a{color:var(--ink)}
.foot a:hover{opacity:.7}
/* reveal */
.rev{opacity:0;transform:translateY(28px);transition:opacity .7s ease,transform .7s ease}
.rev.in{opacity:1;transform:none}
::selection{background:#1C1956;color:#F4F3F3}
/* hero signal hairline + word settle */
.hairline{height:2px;width:min(560px,72%);margin:4px 0 0;border-radius:2px;background:linear-gradient(90deg,#32BFFC,#3D76E8,#6060BE,#B55CB7,#1C1956);background-size:300% 100%;transform:scaleX(0);transform-origin:left;animation:hlDraw .9s cubic-bezier(.16,1,.3,1) .35s forwards, hlDrift 18s ease-in-out 1.6s infinite}
@keyframes hlDraw{to{transform:scaleX(1)}}
@keyframes hlDrift{0%,100%{background-position:0% 50%}50%{background-position:100% 50%}}
.word{display:inline-block;opacity:0;transform:translateY(.5em);filter:blur(6px);transition:opacity .7s cubic-bezier(.16,1,.3,1),transform .7s cubic-bezier(.16,1,.3,1),filter .7s ease}
.word.in{opacity:1;transform:none;filter:none}
/* show more */
.morewrap{text-align:center;margin-top:34px}
.morebtn{font:800 14px/1 'Apparat',Arial,sans-serif;color:var(--ink);background:var(--glass);border:1px solid var(--gline);border-radius:999px;padding:14px 32px;cursor:pointer;backdrop-filter:blur(10px);-webkit-backdrop-filter:blur(10px);transition:transform .18s,box-shadow .18s}
.morebtn:hover{transform:translateY(-2px);box-shadow:0 10px 26px rgba(28,25,86,.14)}
.endnote{margin-top:26px;text-align:center;font-weight:600;font-size:14px;color:var(--mut)}
.endnote a{color:var(--ink);font-weight:800;border-bottom:2px solid rgba(28,25,86,.28)}
.emptynote{grid-column:1/-1;text-align:center;padding:38px 0;font-weight:600;font-size:15px;color:var(--mut)}
.emptynote a{color:var(--ink);font-weight:800;border-bottom:2px solid rgba(28,25,86,.28)}
/* services */
.sintro{font-weight:500;font-size:clamp(15px,1.5vw,18px);line-height:1.6;color:var(--mut);max-width:62ch;margin-bottom:26px}
.sintro b{color:var(--ink);font-weight:700}
.svc{display:grid;grid-template-columns:repeat(3,1fr);gap:20px}
@media(max-width:900px){.svc{grid-template-columns:1fr 1fr}}
@media(max-width:600px){.svc{grid-template-columns:1fr}}
.svc .it{background:var(--glass);border:1px solid var(--gline);border-radius:20px;padding:24px;backdrop-filter:blur(14px);-webkit-backdrop-filter:blur(14px);transition:transform .3s,box-shadow .3s,border-color .3s}
.svc .it:hover{transform:translateY(-4px);box-shadow:0 18px 40px rgba(28,25,86,.12);border-color:rgba(96,96,190,.5)}
.svc .it h3{font-weight:900;font-size:18px;letter-spacing:-.01em;color:var(--ink);margin-bottom:8px}
.svc .it p{font-weight:500;font-size:14px;line-height:1.55;color:var(--body)}
.steps{display:grid;grid-template-columns:repeat(4,1fr);gap:16px}
@media(max-width:900px){.steps{grid-template-columns:1fr 1fr}}
@media(max-width:520px){.steps{grid-template-columns:1fr}}
.step{background:var(--glass);border:1px solid var(--gline);border-radius:18px;padding:20px;backdrop-filter:blur(12px)}
.step .n{font-weight:900;font-size:22px;letter-spacing:-.02em;background:linear-gradient(135deg,#3D76E8,#B55CB7);-webkit-background-clip:text;background-clip:text;color:transparent}
.step h4{font-weight:800;font-size:15px;color:var(--ink);margin:6px 0 4px}
.step p{font-weight:500;font-size:13px;line-height:1.5;color:var(--mut)}
.results{display:flex;flex-wrap:wrap;gap:12px}
.chipr{display:flex;align-items:center;gap:10px;background:var(--glass);border:1px solid var(--gline);border-radius:999px;padding:12px 20px;font-weight:700;font-size:14px;color:var(--ink)}
.chipr::before{content:'';width:9px;height:9px;border-radius:50%;background:linear-gradient(135deg,#32BFFC,#B55CB7);flex:none}
.next-line{margin-top:12px;font-weight:500;font-size:12.5px;color:var(--mut)}
.reply-line{margin-top:6px;font-weight:600;font-size:13px;color:var(--ink);opacity:.82}
/* timed kit offer */
.koffer{position:fixed;right:20px;bottom:20px;z-index:150;max-width:340px;background:#F4F3F3;border:1px solid var(--gline);border-radius:20px;box-shadow:0 28px 70px rgba(28,25,86,.3);padding:22px 22px 20px;transform:translateY(150%);opacity:0;transition:transform .5s cubic-bezier(.16,1,.3,1),opacity .5s ease}
.koffer.show{transform:none;opacity:1}
.koffer .kx{position:absolute;top:10px;right:12px;border:0;background:none;font:800 20px/1 Arial;color:var(--mut);cursor:pointer}
.koffer .ke{font-weight:800;font-size:11px;letter-spacing:.12em;color:var(--mut);margin-bottom:8px}
.koffer h4{font-weight:900;font-size:19px;letter-spacing:-.01em;color:var(--ink);line-height:1.15}
.koffer p{margin:8px 0 14px;font-weight:500;font-size:13px;line-height:1.5;color:var(--body)}
.koffer form{display:flex;gap:8px;flex-wrap:wrap}
.koffer input[type=email]{flex:1;min-width:150px;border:1px solid rgba(28,25,86,.16);border-radius:999px;padding:11px 16px;font:500 14px 'Apparat',Arial,sans-serif;background:#fff;outline:none}
.koffer button.kb{border:0;border-radius:999px;padding:11px 18px;font-weight:800;font-size:14px;color:#F4F3F3;background:linear-gradient(90deg,#3D76E8,#6060BE 55%,#B55CB7);cursor:pointer}
.koffer .later{display:block;margin-top:10px;font-weight:600;font-size:12px;color:var(--mut);background:none;border:0;cursor:pointer;padding:0}
.koffer .kok{display:none;font-weight:700;font-size:14px;color:var(--ink);line-height:1.5}
@media(max-width:520px){.koffer{left:14px;right:14px;max-width:none;bottom:14px}}
/* sticky mini cta */
.mini{position:fixed;right:20px;top:78px;z-index:45;display:none;align-items:center;gap:12px;background:rgba(244,243,243,.92);backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);border:1px solid var(--gline);border-radius:999px;padding:9px 10px 9px 18px;box-shadow:0 12px 30px rgba(28,25,86,.16);font-weight:700;font-size:13px;color:var(--ink)}
.mini.show{display:flex}
.mini a{color:#F4F3F3;background:linear-gradient(90deg,#3D76E8,#6060BE 55%,#B55CB7);font-weight:800;font-size:13px;padding:9px 16px;border-radius:999px}
.mini .mx{border:0;background:none;color:var(--mut);font:800 18px/1 Arial;cursor:pointer}
@media(max-width:820px){.mini{left:14px;right:14px;top:auto;bottom:14px;justify-content:space-between}}
/* page cubes */
.pager{display:flex;gap:8px;justify-content:center;flex-wrap:wrap;margin-top:30px}
.cube{min-width:42px;height:42px;padding:0 12px;border-radius:12px;border:1px solid var(--gline);background:var(--glass);font:800 15px/1 'Apparat',Arial,sans-serif;color:var(--ink);cursor:pointer;backdrop-filter:blur(10px);-webkit-backdrop-filter:blur(10px);display:grid;place-items:center;transition:transform .18s,box-shadow .18s}
.cube:hover{transform:translateY(-2px);box-shadow:0 8px 20px rgba(28,25,86,.14)}
.cube.on{color:#F4F3F3;background:linear-gradient(135deg,#3D76E8,#6060BE 55%,#B55CB7);border-color:transparent;box-shadow:0 8px 22px rgba(96,96,190,.34)}
@media(prefers-reduced-motion:reduce){.rev{opacity:1;transform:none}.blob{animation:none}.card:hover .ph{transform:none}.slide{transition:opacity .3s}.slide.on img{transform:none}html{scroll-behavior:auto}.word{opacity:1;transform:none;filter:none}.hairline{animation:none;transform:scaleX(1)}.koffer{transition:opacity .3s}.kit::after{display:none}.card.reveal-new{animation:none}}
"""

JS = r"""
function track(n,d){try{(window.dataLayer=window.dataLayer||[]).push(Object.assign({event:n},d||{}));if(window.plausible)window.plausible(n);}catch(e){}}
var reduce=matchMedia('(prefers-reduced-motion:reduce)').matches;
var pb=document.querySelector('.prog');
var nav=document.querySelector('.nav');
addEventListener('scroll',function(){var h=document.documentElement;var p=h.scrollTop/(h.scrollHeight-h.clientHeight);pb.style.width=(p*100)+'%';nav.classList.toggle('scrolled',h.scrollTop>10);},{passive:true});
var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){e.target.classList.add('in');io.unobserve(e.target);}});},{threshold:.12});
document.querySelectorAll('.rev').forEach(function(el){io.observe(el);});
// hamburger
var tgl=document.querySelector('.navtoggle'),mob=document.getElementById('mobmenu');
if(tgl){tgl.addEventListener('click',function(){var open=mob.classList.toggle('open');tgl.setAttribute('aria-expanded',open);});
 mob.querySelectorAll('a').forEach(function(a){a.addEventListener('click',function(){mob.classList.remove('open');tgl.setAttribute('aria-expanded','false');});});}
// faq
document.querySelectorAll('.qa button').forEach(function(b){b.addEventListener('click',function(){var qa=b.parentElement,a=qa.querySelector('.ans');var open=qa.classList.toggle('open');b.setAttribute('aria-expanded',open);a.setAttribute('aria-hidden',!open);a.style.maxHeight=open?a.scrollHeight+'px':0;});});
// paginated grids: 6 per sheet, page cubes swap in-zone (no full-page scroll)
function makePager(gridId,pagerId){
  var grid=document.getElementById(gridId),pager=document.getElementById(pagerId);
  if(!grid||!pager)return null;
  var cards=[].slice.call(grid.querySelectorAll('.card')),PAGE=6,page=0,filter='';
  function vis(){return cards.filter(function(c){return !filter||((' '+c.dataset.cat+' ').indexOf(' '+filter+' ')>-1);});}
  function render(){
    var v=vis(),pages=Math.max(1,Math.ceil(v.length/PAGE));if(page>=pages)page=pages-1;if(page<0)page=0;
    cards.forEach(function(c){c.classList.add('hide');});
    v.slice(page*PAGE,page*PAGE+PAGE).forEach(function(c){c.classList.remove('hide');c.classList.remove('reveal-new');void c.offsetWidth;c.classList.add('reveal-new');});
    pager.innerHTML='';
    if(pages>1){for(var i=0;i<pages;i++){(function(i){var b=document.createElement('button');b.type='button';b.className='cube'+(i===page?' on':'');b.textContent=i+1;b.setAttribute('aria-label','Page '+(i+1));if(i===page)b.setAttribute('aria-current','page');b.onclick=function(){if(i===page)return;page=i;render();};pager.appendChild(b);})(i);}}
    return v.length;
  }
  return {render:render,setFilter:function(f){filter=f;page=0;return render();},el:grid};
}
var pills=document.querySelectorAll('.fpill');
var cnt=document.getElementById('fcount');
var empty=document.getElementById('emptynote');
var latest=makePager('grid','pagerLatest');
function refreshLatest(n){if(cnt)cnt.textContent=n+(n===1?' story':' stories');if(empty)empty.style.display=n?'none':'block';}
if(latest)refreshLatest(latest.render());
pills.forEach(function(p){p.addEventListener('click',function(){
  pills.forEach(function(x){x.classList.remove('on');x.setAttribute('aria-pressed','false');});
  p.classList.add('on');p.setAttribute('aria-pressed','true');
  var g=latest?latest.el:null;if(g)g.style.opacity=.35;
  if(latest)refreshLatest(latest.setFilter(p.dataset.f));
  track('filter',{cat:p.dataset.f||'all'});setTimeout(function(){if(g)g.style.opacity=1;},150);
});});
var va=document.getElementById('viewall');if(va)va.addEventListener('click',function(e){e.preventDefault();var all=document.querySelector('.fpill[data-f=""]');if(all)all.click();});
var signals=makePager('sgrid','pagerSignals');if(signals)signals.render();
(function(){var pc=new URLSearchParams(location.search).get('cat');if(!pc)return;var t=null;pills.forEach(function(x){if(x.dataset.f===pc)t=x;});if(t){t.click();setTimeout(function(){var el=document.getElementById('latest');if(el)el.scrollIntoView();},80);}})();
// carousel
(function(){
  var track=document.querySelector('.track');if(!track)return;
  var slides=[].slice.call(track.children),dots=[].slice.call(document.querySelectorAll('.cdot')),i=0,timer=null;
  var ring=document.querySelector('.cring .fill');
  function restartRing(){if(!ring||reduce)return;ring.classList.remove('run');ring.getBoundingClientRect();ring.style.animationPlayState='running';ring.classList.add('run');}
  function render(){
    slides.forEach(function(s,k){var on=k===i;s.classList.toggle('on',on);s.setAttribute('aria-hidden',!on);
      s.querySelectorAll('a').forEach(function(a){a.tabIndex=on?0:-1;});});
    dots.forEach(function(d,k){d.classList.toggle('on',k===i);d.setAttribute('aria-selected',k===i);});
    restartRing();}
  function go(n){i=(n+slides.length)%slides.length;render();}
  function stop(){if(timer){clearInterval(timer);timer=null;}if(ring)ring.style.animationPlayState='paused';}
  function start(){stop();if(reduce||document.hidden)return;restartRing();timer=setInterval(function(){go(i+1);},4000);}
  var nx=document.querySelector('.cnext'),pv=document.querySelector('.cprev');
  if(nx)nx.onclick=function(){go(i+1);start();};
  if(pv)pv.onclick=function(){go(i-1);start();};
  dots.forEach(function(d,k){d.onclick=function(){go(k);start();};});
  var car=document.querySelector('.carousel');
  car.addEventListener('mouseenter',stop);car.addEventListener('mouseleave',start);
  car.addEventListener('focusin',stop);car.addEventListener('focusout',start);
  document.addEventListener('visibilitychange',function(){document.hidden?stop():start();});
  var x0=null;
  car.addEventListener('pointerdown',function(e){x0=e.clientX;});
  car.addEventListener('pointerup',function(e){if(x0===null)return;var dx=e.clientX-x0;if(Math.abs(dx)>40){dx<0?go(i+1):go(i-1);start();}x0=null;});
  render();start();
})();
// shared form submit (Netlify Forms on deploy; graceful in local preview)
function sigSubmit(form,done){
  var pre=location.protocol==='file:'||/^(localhost$|127\.|192\.168\.)/.test(location.hostname);
  if(pre){done(true);return;}
  var data=new URLSearchParams(new FormData(form));
  fetch('/',{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},body:data.toString()})
   .then(function(r){done(r.ok);}).catch(function(){done(false);});
}
// subscribe (home)
var sform=document.getElementById('subform');
if(sform){sform.addEventListener('submit',function(e){e.preventDefault();track('subscribe_submit');
  sigSubmit(sform,function(ok){sform.style.display='none';var m=document.getElementById('subok');
   m.textContent=ok?"You're in. The next edition lands in your inbox.":"Something went wrong. Email hello@sensalab.io and we'll add you.";m.style.display='block';});});}
// free-kit modal
(function(){
  var modal=document.getElementById('kitmodal');if(!modal)return;
  var nameEl=document.getElementById('kitname'),field=document.getElementById('kitfield');
  var form=document.getElementById('kitform'),thanks=document.getElementById('kitthanks'),view=document.getElementById('kitview');
  var lastFocus=null;
  function open(title,name){nameEl.textContent=title;field.value=name;view.href='kit-'+name+'.html';
    form.style.display='';thanks.style.display='none';modal.classList.add('show');lastFocus=document.activeElement;
    track('kit_open',{kit:name});setTimeout(function(){var e=document.getElementById('kitemail');if(e)e.focus();},80);}
  function close(){modal.classList.remove('show');if(lastFocus)lastFocus.focus();}
  document.querySelectorAll('.kit').forEach(function(k){k.addEventListener('click',function(){open(k.dataset.kit,k.dataset.name);});});
  document.getElementById('kitclose').onclick=close;
  modal.addEventListener('click',function(e){if(e.target===modal)close();});
  addEventListener('keydown',function(e){if(e.key==='Escape'&&modal.classList.contains('show'))close();
    if(e.key==='Tab'&&modal.classList.contains('show')){var f=modal.querySelectorAll('button,input,a[href]');if(!f.length)return;var a=f[0],b=f[f.length-1];
      if(e.shiftKey&&document.activeElement===a){b.focus();e.preventDefault();}else if(!e.shiftKey&&document.activeElement===b){a.focus();e.preventDefault();}}});
  form.addEventListener('submit',function(e){e.preventDefault();track('kit_submit',{kit:field.value});
    sigSubmit(form,function(ok){form.style.display='none';thanks.style.display='block';
      thanks.querySelector('p').textContent=ok?'Thanks. Your kit is ready, open it now and we will keep you posted.':'Open your kit below. If the email did not go through, write to hello@sensalab.io.';});});
})();
// ambient motes (elegant drifting light dust, intensifies near the capture section)
(function(){var cv=document.getElementById('motes');if(!cv)return;var ctx=cv.getContext('2d'),dpr=Math.min(devicePixelRatio||1,2),W=0,H=0,motes=[],sprites={};
 var COLORS=[['#3D76E8',35],['#6060BE',30],['#32BFFC',15],['#B55CB7',12],['#1C1956',8]];
 function pick(){var r=Math.random()*100,a=0;for(var k=0;k<COLORS.length;k++){a+=COLORS[k][1];if(r<=a)return COLORS[k][0];}return COLORS[0][0];}
 function sprite(col){if(sprites[col])return sprites[col];var s=document.createElement('canvas'),d=48;s.width=s.height=d;var c=s.getContext('2d'),g=c.createRadialGradient(d/2,d/2,0,d/2,d/2,d/2);g.addColorStop(0,col);g.addColorStop(1,'rgba(255,255,255,0)');c.fillStyle=g;c.beginPath();c.arc(d/2,d/2,d/2,0,7);c.fill();sprites[col]=s;return s;}
 function mk(){var far=Math.random()<0.2,r=(1+Math.random()*2.5)*(far?1.8:1);return {x:Math.random()*W,y:Math.random()*H,r:r,c:pick(),sp:(6+Math.random()*8)*(far?0.5:1),ang:-Math.PI/9+(Math.random()-0.5)*Math.PI/6,seed:Math.random()*99,base:(0.06+Math.random()*0.10)*(far?0.6:1)};}
 function resize(){W=cv.clientWidth;H=cv.clientHeight;cv.width=W*dpr;cv.height=H*dpr;ctx.setTransform(dpr,0,0,dpr,0,0);var n=Math.max(24,Math.min(72,Math.round(W*H/28000)));motes=[];for(var k=0;k<n;k++)motes.push(mk());}
 var energy=0,target=0,last=0;
 function frame(t){if(cv._stop)return;if(!last)last=t;var dt=Math.min(64,t-last)/1000;last=t;energy+=(target-energy)*Math.min(1,dt*3);ctx.clearRect(0,0,W,H);
  for(var k=0;k<motes.length;k++){var m=motes[k];m.x+=Math.cos(m.ang)*m.sp*dt+Math.sin(t/1000*0.3+m.seed)*0.15;m.y+=Math.sin(m.ang)*m.sp*dt;
   if(m.x<-40)m.x=W+40;if(m.x>W+40)m.x=-40;if(m.y<-40)m.y=H+40;if(m.y>H+40)m.y=-40;
   var br=0.7+0.3*(0.5+0.5*Math.sin(t/1000*0.5+m.seed)),a=Math.min(0.26,m.base*br*(1+energy*0.6)),d=m.r*6;
   ctx.globalAlpha=a;ctx.drawImage(sprite(m.c),m.x-d/2,m.y-d/2,d,d);}
  ctx.globalAlpha=1;requestAnimationFrame(frame);}
 addEventListener('resize',function(){clearTimeout(cv._t);cv._t=setTimeout(resize,200);});
 resize();
 if(reduce){for(var k=0;k<motes.length;k++){var m=motes[k],d=m.r*6;ctx.globalAlpha=m.base*0.6;ctx.drawImage(sprite(m.c),m.x-d/2,m.y-d/2,d,d);}ctx.globalAlpha=1;return;}
 document.addEventListener('visibilitychange',function(){cv._stop=document.hidden;if(!document.hidden){last=0;requestAnimationFrame(frame);}});
 requestAnimationFrame(frame);
 var cap=document.getElementById('subscribe');if(cap&&'IntersectionObserver'in window){new IntersectionObserver(function(es){es.forEach(function(e){target=e.isIntersecting?1:0;});},{threshold:.35}).observe(cap);}})();
// hero word settle
(function(){var el=document.querySelector('h1.lede');if(!el)return;var words=el.textContent.trim().split(/\s+/);
 el.innerHTML=words.map(function(w){return '<span class="word">'+w+'</span>';}).join(' ');
 var ws=el.querySelectorAll('.word');if(reduce){ws.forEach(function(w){w.classList.add('in');});return;}
 ws.forEach(function(w,k){setTimeout(function(){w.classList.add('in');},120+k*70);});})();
// timed kit offer (once per session, ~10s, stack-aware)
(function(){var o=document.getElementById('koffer');if(!o)return;
 if(sessionStorage.getItem('sensalab_kit_offer_seen')||localStorage.getItem('sensalab_kit_done'))return;
 var form=o.querySelector('form'),okm=o.querySelector('.kok');
 function show(){if(document.querySelector('.modal.show')){setTimeout(show,2500);return;}o.classList.add('show');track('kit_offer_show');}
 setTimeout(show,10000);
 function close(){o.classList.remove('show');sessionStorage.setItem('sensalab_kit_offer_seen','1');}
 o.querySelector('.kx').onclick=close;o.querySelector('.later').onclick=close;
 addEventListener('keydown',function(e){if(e.key==='Escape'&&o.classList.contains('show'))close();});
 document.addEventListener('click',function(e){if(o.classList.contains('show')&&!o.contains(e.target))close();},true);
 form.addEventListener('submit',function(e){e.preventDefault();track('kit_offer_submit');
  sigSubmit(form,function(ok){form.style.display='none';okm.style.display='block';okm.textContent=ok?'Check your inbox, the kit is on its way.':'Thanks. Email hello@sensalab.io if it does not arrive.';localStorage.setItem('sensalab_kit_done','1');});});})();
// sticky mini cta (after hero scrolls out)
(function(){var mini=document.getElementById('mini');if(!mini)return;if(sessionStorage.getItem('sensalab_mini_dismiss'))return;
 var hero=document.querySelector('.hero');
 if(hero&&'IntersectionObserver'in window){new IntersectionObserver(function(es){if(mini._off)return;es.forEach(function(e){mini.classList.toggle('show',!e.isIntersecting);});},{threshold:0}).observe(hero);}
 mini.querySelector('.mx').onclick=function(){mini._off=1;mini.classList.remove('show');sessionStorage.setItem('sensalab_mini_dismiss','1');};})();
"""

# ---- fragments ----
# newest first, so the freshly compiled real news (edition 21) lead the grid + carousel
STORIES_N = sorted(STORIES, key=lambda s: -s["edition"])
CAROUSEL_N = STORIES_N[:5]
stories_html="".join(
 '<article class="card rev" data-cat="%s"><a class="phwrap" href="%s" aria-label="%s"><div class="ph" style="background-image:url(%s)"></div></a>'
 '<div class="cin"><span class="chip">%s</span><h3><a href="%s">%s</a></h3>'
 '<p class="sum">%s</p>'
 '<div class="cmeta"><span class="dt">Edition %d</span><a class="rd" href="%s">Read &#8594;</a></div>'
 '</div></article>' % (s["tokens"], art(s["slug"]), html.escape(s["headline"]), s["img"], s["cat"], art(s["slug"]), html.escape(s["headline"]), html.escape(s["summary"]), s["edition"], art(s["slug"]))
 for s in STORIES_N)

# Signals: feed diario de noticias reales (Carril 1). Reusa la estética .card pero linkea a la
# fuente (target=_blank + rel=noopener). Grid propio (#sgrid), ajeno a los filtros de #grid.
signals_html="".join(
 '<article class="card rev"><a class="phwrap" href="%s" target="_blank" rel="noopener" aria-label="%s (opens source)"><div class="ph" style="background-image:url(%s)"></div></a>'
 '<div class="cin"><span class="chip">%s</span><h3><a href="%s" target="_blank" rel="noopener">%s</a></h3>'
 '<p class="sum">%s</p>'
 '<div class="cmeta"><span class="dt">%s</span><a class="rd" href="%s" target="_blank" rel="noopener">Read at source &#8599;</a></div>'
 '</div></article>' % (s["link"], html.escape(s["headline"]), s["img"], html.escape(s["cat"]), s["link"], html.escape(s["headline"]), html.escape(s["take"] or s["cat"]), html.escape(s["source"] or "Source"), s["link"])
 for s in SIGNALS)

signals_section = ('<section class="wrap" id="signals"><div class="shead"><h2>Signals</h2>'
 '<span class="m">Real moves, refreshed daily</span></div>'
 '<p class="dek" style="margin-bottom:24px;max-width:64ch">Straight from the wires: what is moving in immersive and experiential right now, each linked to its source. Our own deep reads sit below in <a href="#latest" style="color:#1C1956;font-weight:700;border-bottom:2px solid rgba(28,25,86,.28)">Latest stories</a>.</p>'
 '<div class="g3" id="sgrid">'+signals_html+'</div><div class="pager" id="pagerSignals"></div></section>') if SIGNALS else ""

chips_html="".join('<button class="fpill%s" data-f="%s" aria-pressed="%s">%s</button>' % (" on" if tok=="" else "", tok, "true" if tok=="" else "false", lab) for lab,tok in FILTERS)

slides_html="".join(
 '<div class="slide%s" aria-hidden="%s"><img src="%s" alt="%s"><div class="fscrim"></div>'
 '<div class="fcard"><span class="fchip">%s &middot; Edition %d</span>'
 '<div class="fh">%s</div><p>%s</p><a class="go" href="%s">Read the story &#8594;</a></div></div>'
 % ((" on" if k==0 else ""), "false" if k==0 else "true", s["img"], html.escape(s["headline"]), s["cat"], s["edition"], html.escape(s["headline"]), html.escape(s["summary"]), art(s["slug"]))
 for k,s in enumerate(CAROUSEL_N))
dots_html="".join('<button class="cdot%s" role="tab" aria-selected="%s" aria-label="Go to slide %d"></button>' % (" on" if k==0 else "", "true" if k==0 else "false", k+1) for k in range(len(CAROUSEL_N)))

kits_html="".join(
 '<button class="kit %s" data-kit="%s" data-name="%s"><span class="kn">10</span><span class="kt">%s</span><span class="kd">%s</span><span class="kgo">Get the kit &#8594;</span></button>'
 % (cls, html.escape(title), name, html.escape(title.replace("10 ","").strip()), html.escape(blurb))
 for name,cls,kid,title,blurb in KITS)

arch_html="".join(
 '<article class="card rev"><a class="phwrap" href="%s" aria-label="Read edition %d, %s"><div class="ph" style="background-image:url(%s)"></div></a>'
 '<div class="cin"><span class="chip">Edition %d</span><h3><a href="%s">%s</a></h3><p class="sum">%s</p>'
 '<div class="cmeta"><span class="dt">%s</span><a class="rd" href="%s">Read the edition &#8594;</a></div></div></article>'
 % (href,n,html.escape(tt),cov,n,href,html.escape(tt),html.escape(su),DATE[n][0],href) for n,tt,su,href,cov in ARCH)

faq_html="".join('<div class="qa"><button aria-expanded="false">%s<span class="plus" aria-hidden="true">+</span></button><div class="ans" aria-hidden="true"><p>%s</p></div></div>' % (html.escape(q),html.escape(a)) for q,a in FAQ)

def _svc(sec):
    sid,title,intro,items = sec
    its="".join('<div class="it"><h3>%s</h3><p>%s</p></div>'%(html.escape(t),html.escape(d)) for t,d in items)
    return ('<section class="wrap rev" id="%s"><div class="shead"><h2>%s</h2></div><p class="sintro">%s</p><div class="svc">%s</div></section>'
            % (sid,html.escape(title),html.escape(intro),its))
whatwedo=_svc(SERVICES[0]); different=_svc(SERVICES[1]); whofor=_svc(SERVICES[2])
steps_html="".join('<div class="step"><span class="n">%s</span><h4>%s</h4><p>%s</p></div>'%(n,html.escape(t),html.escape(d)) for n,t,d in HOWWEWORK)
howsection=('<section class="wrap rev" id="how-we-work"><div class="shead"><h2>How we work</h2></div>'
 '<p class="sintro">One method, eight steps, from the goal to the show floor. Everything we build is scalable, reusable, and adaptable across events, cities, and campaigns.</p>'
 '<div class="steps">'+steps_html+'</div></section>')
resultsection=('<section class="wrap rev" id="results"><div class="shead"><h2>Expected results</h2></div>'
 '<p class="sintro">What a SensaLab experience is built to deliver.</p>'
 '<div class="results">'+"".join('<span class="chipr">%s</span>'%html.escape(r) for r in RESULTS)+'</div></section>')

blogposts=",".join(
 '{"@type":"BlogPosting","headline":"%s","datePublished":"%s","url":"https://signal.sensalab.io/%s","author":{"@id":"https://signal.sensalab.io/#org"},"description":"%s"}'
 % (s["headline"].replace('"',"'"), DATE[s["edition"]][1], art(s["slug"]), s["meta"].replace('"',"'")) for s in STORIES)

JSONLD = ('{"@context":"https://schema.org","@graph":['
 '{"@type":["Organization","ProfessionalService"],"@id":"https://signal.sensalab.io/#org","name":"SensaLab","alternateName":["Sensa Lab","SensaLab Studio","SensaLab Los Angeles"],"legalName":"SensaLab","url":"https://sensalab.io/","email":"hello@sensalab.io","logo":"https://signal.sensalab.io/icon-192.png","image":"https://signal.sensalab.io/og.jpg","slogan":"Rendering imagination","description":"SensaLab is a Los Angeles experiential creative studio: the white label real time 3D and immersive layer that agencies and brands use to design and build interactive activations under their own name.","foundingLocation":{"@type":"Place","name":"Los Angeles, California, United States"},"address":{"@type":"PostalAddress","addressLocality":"Los Angeles","addressRegion":"CA","addressCountry":"US"},"areaServed":[{"@type":"Country","name":"United States"},{"@type":"Place","name":"Worldwide"}],"sameAs":["https://instagram.com/sensalab","https://www.linkedin.com/company/sensalab","https://youtube.com/@sensalab","https://sensalab.io/"],"knowsAbout":["Experiential marketing","Immersive experiences","Real time 3D","Virtual production","LED volumes","Brand activations","Spatial computing","Augmented reality","Interactive installations","White label production","BTL marketing","Live events"],"makesOffer":{"@type":"Offer","itemOffered":{"@type":"Service","name":"White label experiential and immersive production","serviceType":"Experiential marketing"}}},'
 '{"@type":"WebSite","@id":"https://signal.sensalab.io/#site","url":"https://signal.sensalab.io/","name":"The Signal","publisher":{"@id":"https://signal.sensalab.io/#org"}},'
 '{"@type":"Blog","@id":"https://signal.sensalab.io/#blog","name":"The Signal","description":"Immersive and experiential marketing news. Real moves every two weeks, with the why it matters.","publisher":{"@id":"https://signal.sensalab.io/#org"},"blogPost":[' + blogposts + ']},'
 '{"@type":"FAQPage","@id":"https://signal.sensalab.io/#faq","mainEntity":['
 + ",".join('{"@type":"Question","name":"%s","acceptedAnswer":{"@type":"Answer","text":"%s"}}' % (q.replace('"',"'"),a.replace('"',"'")) for q,a in FAQ)
 + ']}]}')

HEAD = ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
 '<meta name="viewport" content="width=device-width,initial-scale=1">'
 '<meta name="color-scheme" content="light only">'
 '<title>The Signal, immersive and experiential marketing news | SensaLab</title>'
 '<meta name="description" content="The Signal is SensaLab\'s biweekly read on immersive and experiential marketing: real moves and why they matter for agency producers and brands.">'
 '<link rel="canonical" href="https://signal.sensalab.io/">'
 '<meta name="robots" content="index,follow,max-image-preview:large">'
 '<link rel="icon" type="image/png" sizes="32x32" href="favicon-32.png"><link rel="apple-touch-icon" href="apple-touch-icon.png">'
 '<meta property="og:type" content="website"><meta property="og:site_name" content="The Signal by SensaLab">'
 '<meta property="og:title" content="The Signal, immersive and experiential marketing news">'
 '<meta property="og:description" content="Real moves in immersive and experiential marketing, every two weeks, with the why it matters.">'
 '<meta property="og:url" content="https://signal.sensalab.io/"><meta property="og:image" content="https://signal.sensalab.io/og.jpg">'
 '<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="The Signal by SensaLab">'
 '<meta name="twitter:description" content="Immersive and experiential marketing news, every two weeks.">'
 '<meta name="twitter:image" content="https://signal.sensalab.io/og.jpg">'
 '<meta name="author" content="SensaLab"><meta name="publisher" content="SensaLab">'
 '<meta name="geo.region" content="US-CA"><meta name="geo.placename" content="Los Angeles"><meta name="theme-color" content="#F4F3F3">'
 '<meta name="keywords" content="experiential marketing, immersive marketing, real time 3D, virtual production, LED volume, brand activation, spatial experiences, augmented reality marketing, white label experiential studio, SensaLab, SensaLab Los Angeles, experiential agency Los Angeles">'
 '<link rel="alternate" type="application/rss+xml" title="The Signal by SensaLab" href="https://signal.sensalab.io/feed.xml">'
 '<script defer data-domain="signal.sensalab.io" src="https://plausible.io/js/script.js"></script>'
 '<script type="application/ld+json">' + JSONLD + '</script>'
 '<style>' + FONT + CSS + '</style></head>')

BODY = ('<body>'
 '<a class="skip" href="#latest">Skip to stories</a>'
 '<div class="prog"></div><div class="bg"><div class="blob b1"></div><div class="blob b2"></div><div class="blob b3"></div></div><canvas id="motes" aria-hidden="true"></canvas>'
 '<header class="nav"><div class="in"><a class="brand" href="#top"><img src="'+ISO+'" alt="SensaLab logo"><b>The Signal</b></a>'
 '<nav class="nlinks" aria-label="Primary"><a href="#latest">Latest</a><a href="#kit">Free kit</a><a href="#faq">FAQ</a></nav>'
 '<div class="cta"><a class="ghost" href="#subscribe">Subscribe</a><a class="solid" href="work.html">Work with us</a></div>'
 '<button class="navtoggle" aria-label="Menu" aria-expanded="false" aria-controls="mobmenu"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"><path d="M3 6h18M3 12h18M3 18h18"/></svg></button>'
 '</div>'
 '<div class="mobmenu" id="mobmenu"><div class="panel"><a href="#latest">Latest</a><a href="#kit">Free kit</a><a href="#faq">FAQ</a><a href="#subscribe">Subscribe</a><a class="solid" href="work.html">Work with us</a></div></div>'
 '</header>'
 '<main id="top">'
 # intro + carousel
 '<section class="wrap" style="padding-top:14px;padding-bottom:0"><div class="rev"><span class="eyebrow"><i></i>The dispatch</span>'
 '<h1 class="lede">The experiential and immersive moves worth your week.</h1><div class="hairline" aria-hidden="true"></div>'
 '<p class="dek"><b>SensaLab is a Los Angeles experiential creative studio, the white label real time 3D and immersive layer that agencies and brands use to build activations under their own name.</b> The Signal is our biweekly briefing on the moves shaping immersive and experiential marketing, each with a clear read on why it matters.</p></div>'
 '<div class="hero rev"><div class="carousel" aria-roledescription="carousel" aria-label="Featured stories"><span class="cap">Featured stories</span>'
 '<div class="track">'+slides_html+'</div>'
 '<button class="cbtn cprev" aria-label="Previous slide">&#8249;</button><button class="cbtn cnext" aria-label="Next slide">&#8250;</button>'
 '<svg class="cring" viewBox="0 0 34 34" aria-hidden="true"><circle class="bg" cx="17" cy="17" r="14"></circle><circle class="fill" cx="17" cy="17" r="14"></circle></svg>'
 '</div><div class="cdots" role="tablist" aria-label="Choose slide">'+dots_html+'</div></div></section>'
 # latest + filters
 '<section class="wrap" id="latest"><div class="shead"><h2>Latest stories</h2><span class="m" id="fcount" aria-live="polite">'+str(len(STORIES))+' stories</span></div>'
 '<div class="filters" id="filters" role="group" aria-label="Filter stories by category">'+chips_html+'</div>'
 '<div class="g3" id="grid" aria-live="polite"><div class="emptynote" id="emptynote" style="display:none">No stories here yet. <a href="#" id="viewall">Try another filter or view all.</a></div>'+stories_html+'</div>'
 '<div class="pager" id="pagerLatest"></div></section>'
 # free kit
 '<section class="wrap" id="kit"><div class="shead"><h2>Free kit with ideas</h2><span class="m">Steal these</span></div>'
 '<p class="dek" style="margin-bottom:26px">Ready to pitch ideas for putting people inside a brand. Pick a kit and we will send you ten, straight to your inbox.</p>'
 '<div class="kits rev">'+kits_html+'</div></section>'
 # hire (conversion)
 '<section class="wrap" id="work"><div class="hire rev"><div class="hin">'
 '<h2>Put people inside your brand</h2>'
 '<p>We build responsive, multisensory, real time experiences for agencies and brands, white label, under your name. From the first idea to the live activation.</p>'
 '<div class="row"><a class="p1" href="work.html">Work with us &#8594;</a>'
 '<a class="p2" href="https://sensalab.io">See what is possible</a></div>'
 '<p class="reply-line">We reply within one business day, from Los Angeles.</p></div></div></section>'
 # faq
 '<section class="wrap" id="faq"><div class="faqwrap">'
 '<div class="faqside"><span class="eyebrow"><i></i>The essentials</span>'
 '<h2>Common questions</h2>'
 '<p>What experiential really means, what we build, and how often The Signal lands in your inbox.</p>'
 '<a class="faqcta" href="mailto:hello@sensalab.io?subject=A%20question%20for%20SensaLab">Still have a question? Talk to us &#8594;</a></div>'
 '<div class="faq rev">'+faq_html+'</div></div></section>'
 # subscribe
 '<section class="wrap" id="subscribe"><div class="subs rev">'
 '<span class="eyebrow"><i></i>The newsletter</span>'
 '<h2>Get The Signal every two weeks</h2>'
 '<p class="sp">Real moves in experiential and real time, each with a clear read on why it matters for your work. Free, no filler.</p>'
 '<form class="form" id="subform" name="signal-subscribe" method="POST" data-netlify="true" netlify-honeypot="bot-field">'
 '<input type="hidden" name="form-name" value="signal-subscribe"><p class="hp"><label>Do not fill this <input name="bot-field"></label></p>'
 '<input type="email" name="email" placeholder="you@studio.com" required aria-label="Your email"><button type="submit">Get The Signal</button></form>'
 '<div class="okmsg" id="subok" role="status"></div>'
 '<p class="reassure">Free forever &middot; every two weeks &middot; unsubscribe anytime</p>'
 '<p class="next-line">What happens next: one useful idea for experiential teams, roughly twice a month, from a real person. No drip spam.</p>'
 '<p class="trust">Read by experiential producers, creative directors and brand teams.</p>'
 '</div></section>'
 # about
 '<section id="about" aria-label="About SensaLab" style="max-width:920px;margin:0 auto;padding:44px 22px 8px">'
 '<h2 style="font-size:13px;letter-spacing:.12em;color:#787878;font-weight:800;margin:0 0 14px">About SensaLab</h2>'
 '<p style="font-size:19px;line-height:1.55;color:#1C1956;font-weight:700;margin:0 0 14px;max-width:720px">SensaLab is a Los Angeles experiential creative studio.</p>'
 '<p style="font-size:16px;line-height:1.7;color:#0B0F0F;margin:0 0 12px;max-width:720px;font-weight:500">We are the white label real time 3D and immersive layer that agencies and brands use to build interactive activations under their own name. We work in real time 3D, virtual production and LED volumes, spatial and augmented experiences, immersive installations and live brand activations, and we ship them white label so the work goes out under your brand, not ours.</p>'
 '<p style="font-size:16px;line-height:1.7;color:#787878;margin:0;max-width:720px;font-weight:500">Based in Los Angeles, California. See more at <a href="https://sensalab.io" style="color:#1C1956;font-weight:700">sensalab.io</a> or write to <a href="mailto:hello@sensalab.io" style="color:#1C1956;font-weight:700">hello@sensalab.io</a>.</p>'
 '</section>'
 '</main>'
 '<footer class="foot"><div class="wrap"><p><b>SensaLab</b></p>'
 '<p>Rendering imagination is the principle that guides everything we do. We turn ideas into emotional, immersive and measurable realities. From Los Angeles.</p>'
 '<p style="margin-top:10px"><a href="https://sensalab.io">sensalab.io</a> &middot; <a href="https://instagram.com/sensalab">Instagram</a> &middot; <a href="https://www.linkedin.com/company/sensalab">LinkedIn</a> &middot; <a href="https://youtube.com/@sensalab">YouTube</a></p>'
 '<p style="margin-top:8px">&#169; 2026 SensaLab &middot; Los Angeles, CA, USA &middot; <a href="mailto:hello@sensalab.io">hello@sensalab.io</a> &middot; <a href="privacy.html">Privacy</a></p>'
 '</div></footer>'
 # sticky mini cta + timed kit offer
 '<div class="mini" id="mini"><span>Building an activation? Let us help.</span><a href="work.html">Work with us</a><button class="mx" aria-label="Dismiss">&times;</button></div>'
 '<div class="koffer" id="koffer" role="dialog" aria-label="Free kit offer"><button class="kx" aria-label="Close">&times;</button>'
 '<span class="ke">Free kit</span><h4>Ten ideas for your next activation</h4>'
 '<p>Grab our free kit, 10 interactive experience concepts you can pitch this quarter. Drop your email and we will send it over.</p>'
 '<form name="signal-kit" method="POST" data-netlify="true" netlify-honeypot="bot-field"><input type="hidden" name="form-name" value="signal-kit"><input type="hidden" name="kit" value="activations"><p class="hp"><label>Do not fill<input name="bot-field"></label></p>'
 '<input type="email" name="email" required placeholder="you@studio.com" aria-label="Your email"><button type="submit" class="kb">Send me the kit</button></form>'
 '<button class="later">Maybe later</button><div class="kok" role="status"></div></div>'
 # modal
 '<div class="modal" id="kitmodal"><div class="mbox" role="dialog" aria-modal="true" aria-labelledby="kitname"><button class="mclose" id="kitclose" aria-label="Close">&times;</button>'
 '<span class="eyebrow"><i></i>Free kit</span><h3 id="kitname">10 ideas</h3>'
 '<p class="mp">Leave your email and we will send the kit and the newsletter. You can open it right away too.</p>'
 '<form class="mform" id="kitform" name="signal-kit" method="POST" data-netlify="true" netlify-honeypot="bot-field">'
 '<input type="hidden" name="form-name" value="signal-kit"><input type="hidden" id="kitfield" name="kit"><p class="hp"><label>Do not fill this <input name="bot-field"></label></p>'
 '<input type="email" id="kitemail" name="email" placeholder="you@studio.com" required aria-label="Your email">'
 '<button type="submit">Send me the kit</button></form>'
 '<div class="mthanks" id="kitthanks"><p>Thanks. Your kit is ready.</p><a id="kitview" href="#">Open your kit &#8594;</a></div></div></div>'
 '<script>'+JS+'</script></body></html>')

(BLOG/"index.html").write_text(HEAD+BODY, encoding="utf-8")
print("wrote", BLOG/"index.html", (len(HEAD)+len(BODY))//1024, "KB", "|", len(STORIES), "stories,", len(CAROUSEL), "slides")
