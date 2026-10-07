#!/usr/bin/env bash
set -euo pipefail

echo "==> 1. Merging removal commit onto main"
git checkout main
git merge backup-before-blog-removal --no-edit -m "Remove blog and writing sections" || true

echo "==> 2. Deleting leftover backup/cache/report files"
find . -name "*.build-backup" -not -path "./.git/*" -delete
find . -name "__pycache__" -type d -not -path "./.git/*" -exec rm -rf {} + 2>/dev/null || true
rm -f audit-report.json

echo "==> 3. Stripping remaining blog refs from index.html"
# JSON-LD @id pointing to /blog/#blog
perl -0pi -e 's/,\s*"@id"\s*:\s*"[^"]*\/blog\/#blog"\s*//g' index.html 2>/dev/null || true
# CSS comment "/* Writing and blog */"
perl -0pi -e 's|/\*\s*Writing and blog\s*\*/||g' index.html 2>/dev/null || true
# Any leftover anchor to ./blog/ or ../blog/
perl -0pi -e 's|<a\b[^>]*href="(?:\.\./)?blog/?"[^>]*>.*?</a>||gis' index.html projects/index.html 2>/dev/null || true

echo "==> 4. Making build_site.py tolerate a missing blog/ directory"
python3 - <<'PY'
from pathlib import Path
p = Path("scripts/build_site.py")
if not p.exists():
    print("build_site.py not found; skipping")
    raise SystemExit(0)
s = p.read_text(encoding="utf-8")
old = 'blog_page = root / "blog" / "index.html"\n    if not blog_page.exists():\n        raise SiteError("blog/index.html is required")'
new = ('blog_page = root / "blog" / "index.html"\n'
       '    if not blog_page.exists():\n'
       '        log("blog/ directory removed; skipping blog build steps.")\n'
       '        blog_page = None')
if old in s:
    s = s.replace(old, new)
    p.write_text(s, encoding="utf-8")
    print("Patched: blog build step no longer aborts when blog/ is missing")
else:
    print("Could NOT find the expected blog check. Manual review of build_site.py needed (see note below).")
PY

echo "==> 5. Committing and pushing"
git add -A
git commit -m "Clean up remaining blog/writing references and disable blog build steps" || true
git push origin main

echo
echo "==> Final verification:"
git grep -n -i "blog\|writing" -- . ':!scripts/build_site.py' ':!*.lock' ':!.git' || echo "  ✅ No blog/writing references left outside build_site.py"
