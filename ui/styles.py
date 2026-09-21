"""Shared CSS matching the black theme + glowing auth."""
import streamlit as st

GLOBAL_CSS = """
<style>
.app{background:#0b0b0b;border-radius:12px;padding:14px;color:#F1EFE8;}
.row{display:flex;gap:10px;margin:0 0 12px;}
.av{flex:none;width:32px;height:32px;border-radius:50%;display:flex;align-items:center;justify-content:center;}
.who{font-size:12px;margin:0 0 3px;}
.bub{border-radius:12px;padding:8px 12px;font-size:13px;line-height:1.5;color:#F1EFE8;background:#2C2C2A;}
.mono{font-family:'SF Mono','Fira Code',monospace;font-size:12px;}
.rd{display:flex;align-items:center;gap:8px;font-size:12px;color:#B4B2A9;margin:4px 0 12px;}
.rd:before,.rd:after{content:"";flex:1;height:0.5px;background:#444441;}
.pill{font-size:12px;padding:3px 10px;border-radius:999px;display:flex;align-items:center;gap:6px;}
.dot{width:7px;height:7px;border-radius:50%;background:currentColor;}
.pulse{animation:p 1.2s ease-in-out infinite;}
@keyframes p{0%,100%{opacity:1}50%{opacity:.25}}
.mt div{background:#2C2C2A;border-radius:10px;padding:8px 12px;}
.mt small{display:block;font-size:12px;color:#B4B2A9;}
.mt b{font-size:20px;font-weight:500;}

.glow-card{
  background:rgba(12,14,18,0.85);
  border-radius:24px;
  padding:28px 26px;
  border:1px solid rgba(55,138,221,0.25);
  box-shadow:0 0 40px rgba(55,138,221,0.15),0 0 80px rgba(55,138,221,0.08),inset 0 0 30px rgba(55,138,221,0.05);
}
.hero-title{
  font-size:44px;font-weight:700;line-height:1.1;letter-spacing:-1px;margin-bottom:16px;
  background:linear-gradient(135deg,#ffffff,#9fc9ff);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
}
.hero-sub{font-size:15px;line-height:1.6;color:#A8B2C0;margin-bottom:24px;}
.terminal-line{
  font-family:'SF Mono','Fira Code',monospace;font-size:12px;line-height:1.7;
  background:#12171f;border-radius:12px;padding:16px 14px;border-left:3px solid #378ADD;
  color:#ced6e0;
}
.badge{font-size:11px;padding:5px 14px;border-radius:999px;border:1px solid #2e3a48;color:#9aa9bc;background:rgba(20,26,34,0.7);}
</style>
"""
