#!/bin/bash
# Hermes Vault Bootstrap — Linux/macOS
# Run once after cloning the vault on a new machine.

set -uo pipefail

# --- Config ---
VAULT_NAME="hermes-vault"
GIT_USER="jasonVPS"
GIT_EMAIL="jason.koslowski@outlook.de"

echo "============================================"
echo "   Hermes Vault Bootstrap (Linux/macOS)"
echo "============================================"

# Find vault directory
if [ -d ".git" ]; then
    VAULT_DIR="$(pwd)"
elif [ -d "$HOME/Documents/$VAULT_NAME/.git" ]; then
    VAULT_DIR="$HOME/Documents/$VAULT_NAME"
elif [ -d "$HOME/Obsidian\ Vaults/$VAULT_NAME/.git" ]; then
    VAULT_DIR="$HOME/Obsidian Vaults/$VAULT_NAME"
else
    echo "ERROR: Could not find $VAULT_NAME Git repository."
    echo "Please run this script from inside your vault folder."
    exit 1
fi

echo "[OK] Vault found at: $VAULT_DIR"
cd "$VAULT_DIR"

# --- 1. Git Identity ---
echo ""
echo "[1/4] Setting Git identity..."
git config --global user.name "$GIT_USER"
git config --global user.email "$GIT_EMAIL"
echo "[OK] Git identity set: $GIT_USER <$GIT_EMAIL>"

# --- 2. Git Remote ---
echo ""
echo "[2/4] Checking Git remote..."
if git remote -v > /dev/null 2>&1; then
    echo "[OK] Remote configured:"
    git remote -v
else
    echo "[WARN] No remote configured."
fi

# --- 3. Fetch/Pull ---
echo ""
echo "[3/4] Testing pull..."
git fetch origin

STATUS=$(git status --short)
if [ -z "$STATUS" ]; then
    echo "[OK] Working tree clean. Pulling latest..."
    git pull origin main || echo "[WARN] Pull had issues."
else
    echo "[INFO] You have local changes. Stashing and pulling..."
    git stash
    git pull origin main
    git stash pop
    echo "[OK] Your local changes were restored."
fi

# --- 4. Push Test ---
echo ""
echo "[4/4] Testing push permissions..."
if git push --dry-run origin main > /dev/null 2>&1; then
    echo "[OK] Push permission OK."
else
    echo "[WARN] Push test failed. Check your SSH key or HTTPS token."
fi

# --- 5. Obsidian Git Plugin Note ---
echo ""
echo "============================================"
echo "  Manual Step: Obsidian Git Plugin"
echo "============================================"
echo ""
echo "In Obsidian:"
echo " 1. Open Settings → Community Plugins → Browse"
echo " 2. Search 'Obsidian Git' and Install/Enable"
echo " 3. In Git Plugin Settings:"
echo "     - Turn ON 'Pull updates on startup'"
echo "     - Turn ON 'Auto commit and sync'"
echo "     - Set interval: 60 seconds"
echo ""
echo "Done! Your vault is ready."
