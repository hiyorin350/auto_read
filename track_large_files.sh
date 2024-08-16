#!/bin/bash

# 50MB以上のファイルを検索してGit LFSで追跡する (.gitディレクトリを除外)
find . -type f -size +50M ! -path "./.git/*" | while read -r file; do
  echo "Tracking large file with Git LFS: $file"
  git lfs track "$file"
done

# .gitattributesファイルをコミット
git add .gitattributes
git commit -m "Automatically tracked large files with Git LFS"
