#!/usr/bin/env bash
# Wrap the dashboard source (the claude.ai artifact file) into a full index.html for GitHub Pages.
# Usage: tools/build_page.sh path/to/source.html   (run from the repo root)
set -euo pipefail
src="$1"
{
  printf '<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
  printf '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
  printf '<link rel="manifest" href="manifest.webmanifest">\n'
  printf '<link rel="apple-touch-icon" href="apple-touch-icon.png">\n'
  printf '<link rel="icon" type="image/png" sizes="192x192" href="icon-192.png">\n'
  printf '<meta name="theme-color" content="#1b2333">\n'
  printf '<meta name="apple-mobile-web-app-capable" content="yes">\n'
  printf '<meta name="apple-mobile-web-app-title" content="AB Dashboard">\n'
  sed -n '1,/<\/style>/p' "$src"
  printf '<style>*,*::before,*::after{box-sizing:border-box}body{margin:0}[hidden]{display:none!important}</style>\n</head>\n<body>\n'
  sed -n '/<\/style>/,$p' "$src" | tail -n +2
  printf '\n</body>\n</html>\n'
} > index.html
echo "index.html built"
