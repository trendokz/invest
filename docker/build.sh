#!/bin/sh
# Собирает страницы в /site. Данные берутся из /data (том), иначе из тестового примера.
set -e
rm -rf /work && mkdir -p /work && cp -r /src/. /work/ && cd /work
if [ -f /data/data.json ]; then cp /data/data.json data.json
else echo "[trendo] /data/data.json не найден, использую data.example.json"; cp example/data.json data.json; fi
if [ -f /data/codes.json ]; then cp /data/codes.json codes.json
else echo "[trendo] /data/codes.json не найден, тестовые коды: AB-1234 (инвестор), ADMIN-CODE (управляющий)"
  cp example/codes.json codes.json; fi
TRENDO_DATA_DIR=/work python3 build.py
mkdir -p /site/cabinet /site/calculator
cp cabinet/index.html /site/cabinet/index.html
cp calculator/index.html /site/calculator/index.html
echo "[trendo] готово"
