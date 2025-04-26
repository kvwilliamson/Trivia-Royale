# Remove the zip file from git history
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch TriviaRoyale-darwin-20250425.zip" \
  --prune-empty --tag-name-filter cat -- --all

# Clean up the refs and garbage collect
git for-each-ref --format='delete %(refname)' refs/original | git update-ref --stdin
git reflog expire --expire=now --all
git gc --prune=now

# Force push the changes
git push origin main --force
