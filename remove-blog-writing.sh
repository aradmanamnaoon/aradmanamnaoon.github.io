#!/usr/bin/env bash
set -euo pipefail

# --- CONFIG ---
BACKUP_BRANCH="backup-before-blog-removal-$(date +%Y%m%d-%H%M%S)"
MAIN_BRANCH=$(git symbolic-ref --short HEAD 2>/dev/null || echo main)

echo "Creating backup branch: $BACKUP_BRANCH"
git checkout -b "$BACKUP_BRANCH" 2>/dev/null || true
git add -A && git commit -m "Backup before blog removal" || true
git push origin "$BACKUP_BRANCH" 2>/dev/null || true
git checkout "$MAIN_BRANCH" 2>/dev/null || git checkout main

# --- 1. REMOVE BLOG/WRITING DIRECTORIES AND FILES ---
echo "Removing blog/writing directories and files..."
for d in blog writing _posts posts articles; do
  if [ -d "$d" ]; then
    rm -rf "$d"
    echo "  Removed directory: $d"
  fi
done

for f in blog.html writing.html blog.md writing.md articles.json feed.xml rss.xml atom.xml blog.xml writing.xml; do
  if [ -f "$f" ]; then
    rm -f "$f"
    echo "  Removed file: $f"
  fi
done

# --- 2. CLEAN REFERENCES IN REMAINING FILES ---
echo "Cleaning references in HTML, XML, TXT, MD, CSS..."
find . -type f \( \
  -name "*.html" -o -name "*.htm" -o -name "*.xml" -o -name "*.txt" -o -name "*.md" \
  -o -name "*.css" -o -name "*.scss" \
\) -not -path "./.git/*" -not -path "./node_modules/*" -not -path "./dist/*" -print0 |
while IFS= read -r -d '' file; do
  if grep -qiE 'blog|writing' "$file"; then
    echo "  Processing: $file"
    # Remove HTML anchor tags linking to blog/writing
    perl -0pi -e 's/<a\b[^>]*href="[^"]*(?:blog|writing)[^"]*"[^>]*>.*?<\/a>//gis' "$file"
    # Remove empty list items left behind
    perl -0pi -e 's/<li>\s*<\/li>//gis' "$file"
    # Remove XML <url> blocks containing blog/writing
    perl -0pi -e 's/<url>.*?(?:blog|writing).*?<\/url>//gis' "$file"
    # For TXT/MD: remove any line containing blog/writing
    if [[ "$file" == *.txt || "$file" == *.md ]]; then
      perl -ni -e 'print unless /(?:blog|writing)/i' "$file"
    fi
  fi
done

# --- 3. COMMIT AND PUSH ---
echo "Committing changes..."
git add -A
git commit -m "Remove blog and writing sections completely" || echo "No changes to commit"
git push origin "$MAIN_BRANCH" 2>/dev/null || git push origin HEAD

echo "Done. Backup branch: $BACKUP_BRANCH"
echo "If anything is broken, restore with: git checkout $BACKUP_BRANCH"
echo "If you have a build step, run it now (e.g., npm run build) and commit the dist/ folder."
