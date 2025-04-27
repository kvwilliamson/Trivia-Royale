# Create a backup branch just in case
git branch backup-main

# Remove the file from git history (more aggressive approach)
git filter-branch -f --index-filter 'git rm --cached --ignore-unmatch TriviaRoyale-darwin-20250425.zip' HEAD

# Remove the original refs
rm -rf .git/refs/original/

# Remove the filter-branch backup
rm -rf .git/refs/original/

# Expire all reflogs
git reflog expire --expire=now --all

# Aggressively garbage collect
git gc --prune=now --aggressive

# Force push with lease (safer than plain force push)
git push origin main --force-with-lease

# List files in the repository
git ls-files | grep TriviaRoyale-darwin
