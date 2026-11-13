#!/bin/bash
# Renders every screen in tools/screens.html to assets/screens/<name>.png (iPhone 1206x2622, Watch 624x744).
cd "$(dirname "$0")"; out=../assets/screens; mkdir -p $out
shoot(){ timeout 90 google-chrome --headless=new --no-sandbox --disable-gpu --hide-scrollbars --virtual-time-budget=5000 --window-size=$2 --screenshot=$out/$1.png "file://$PWD/screens.html?s=$1&z=${3:-3}" 2>/dev/null; }
for s in home-saved home-today setup-interval setup-repeat setup-custom home workout zones logex lock calendar meals exercises strength byweight; do shoot $s 1206,2622 & done; wait
for s in watch-done watch-controls watch-active watch-rest watch-repeat; do shoot $s 624,744 & done; wait
for s in duo-open duo-book; do shoot $s 1780,1252 2 & done; for s in duo-upright duo-bench; do shoot $s 1252,1780 2 & done; shoot duo-closed 932,1356 2 & wait
