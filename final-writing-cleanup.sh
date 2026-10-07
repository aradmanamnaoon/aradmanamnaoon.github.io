#!/usr/bin/env bash
set -euo pipefail

echo "==> 1. Removing helper scripts"
rm -f remove-blog-writing.sh finish-blog-removal.sh

echo "==> 2. Stripping Writing section + CSS + JSON-LD from index.html"
python3 - <<'PY'
import re
from pathlib import Path

p = Path("index.html")
s = p.read_text(encoding="utf-8")
original_len = len(s)

# (a) JSON-LD @id pointing to /blog/#blog
s = re.sub(r'\s*"@id"\s*:\s*"[^"]*\/blog\/#blog"\s*,?', '', s)

# (b) CSS comment
s = re.sub(r'\s*/\*\s*Writing and blog\s*\*/\s*', '\n', s)

# (c) CSS rules whose selectors start with .writing-
# Handles grouped selectors like ".writing-meta,\n      .writing-title {" too.
s = re.sub(
    r'[ \t]*(?:\.writing-[\w-]+\s*,\s*)*\.writing-[\w-]+\s*\{[^{}]*\}\s*',
    '', s)

# (d) Entire <section id="writing"> … </section> block
m = re.search(r'[ \t]*<section\b[^>]*\bid="writing"[^>]*>', s)
if m:
    start = m.start()
    pos = m.start()
    depth = 0
    while pos < len(s):
        mm = re.search(r'</?section\b', s[pos:])
        if not mm:
            break
        idx = pos + mm.start()
        if s[idx:idx+2] == '</':
            depth -= 1
            if depth == 0:
                end = s.find('>', idx) + 1
                s = s[:start] + s[end:]
                break
        else:
            depth += 1
        pos = idx + 2
else:
    print("  (no <section id=\"writing\"> found — already gone?)")

# (e) Collapse runs of blank lines left behind
s = re.sub(r'\n{3,}', '\n\n', s)

p.write_text(s, encoding="utf-8")
print(f"  index.html: {original_len} -> {len(s)} bytes")
PY

echo "==> 3. Committing and pushing"
git add -A
git commit -m "Remove Writing section, CSS, and JSON-LD from homepage" || echo "Nothing to commit"
git push origin main

echo
echo "==> Final check:"
git grep -n -i "blog\|writing" -- . ':!scripts/build_site.py' ':!.git' || \
  echo "  ✅ No blog/writing references left outside scripts/build_site.py"
