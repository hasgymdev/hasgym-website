#!/bin/bash
# usage: shoot.sh page.html[?query] out.png [height]
cd "$(dirname "$0")"
timeout 120 google-chrome --headless=new --no-sandbox --disable-gpu --hide-scrollbars --virtual-time-budget=14000 --window-size=1280,${3:-7000} --screenshot="$2" "file://$PWD/$1" 2>/dev/null
python3 - "$2" <<'PY'
import sys
from PIL import Image
import numpy as np
p=sys.argv[1];im=Image.open(p).convert('RGB');a=np.asarray(im).astype(int);h=a.shape[0];last=a[-1]
while h>1 and abs(a[h-1]-last).max()<3: h-=1
im=im.crop((0,0,im.width,min(im.height,h+2)));im.save(p);print(p,im.size)
n=-(-im.height//1700)
for i in range(n): im.crop((0,i*im.height//n,im.width,(i+1)*im.height//n)).save(p.replace('.png',f'-{i+1}.png'))
PY
