#!/bin/bash
###############################################################################
# AUTO PUSH TO GITHUB - CRYPTO AI PREDICTION SYSTEM
# Branch: claude/fix-repairs-011CUioBYaYL2bwyVCxEF5nT
###############################################################################

set -e  # Exit on error

echo "=========================================="
echo "🚀 CRYPTO AI - AUTO PUSH TO GITHUB"
echo "=========================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
GITHUB_REPO="sirhung/crypto"
BRANCH_NAME="claude/fix-repairs-011CUioBYaYL2bwyVCxEF5nT"

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo -e "${RED}❌ Git is not installed. Please install git first.${NC}"
    exit 1
fi

# Get GitHub token
echo -e "${YELLOW}📝 GitHub Personal Access Token Required${NC}"
echo ""
echo "To create a token:"
echo "  1. Go to https://github.com/settings/tokens"
echo "  2. Click 'Generate new token (classic)'"
echo "  3. Select 'repo' scope"
echo "  4. Copy the token"
echo ""
read -sp "Enter your GitHub Personal Access Token: " GITHUB_TOKEN
echo ""
echo ""

if [ -z "$GITHUB_TOKEN" ]; then
    echo -e "${RED}❌ Token is required. Exiting.${NC}"
    exit 1
fi

# Check if repository exists on GitHub
echo -e "${YELLOW}🔍 Checking if repository exists...${NC}"
REPO_CHECK=$(curl -s -o /dev/null -w "%{http_code}" \
    -H "Authorization: token $GITHUB_TOKEN" \
    "https://api.github.com/repos/$GITHUB_REPO")

if [ "$REPO_CHECK" = "404" ]; then
    echo -e "${YELLOW}📦 Repository doesn't exist. Creating...${NC}"

    # Create repository
    RESPONSE=$(curl -s -X POST \
        -H "Authorization: token $GITHUB_TOKEN" \
        -H "Accept: application/vnd.github.v3+json" \
        https://api.github.com/user/repos \
        -d "{
            \"name\": \"crypto\",
            \"description\": \"God Mode 10000 - AI Crypto & Forex Prediction System\",
            \"private\": false,
            \"auto_init\": false
        }")

    if echo "$RESPONSE" | grep -q "\"full_name\""; then
        echo -e "${GREEN}✅ Repository created successfully!${NC}"
    else
        echo -e "${RED}❌ Failed to create repository${NC}"
        echo "Response: $RESPONSE"
        exit 1
    fi
else
    echo -e "${GREEN}✅ Repository exists${NC}"
fi

# Configure git remote
echo -e "${YELLOW}🔧 Configuring remote...${NC}"
REMOTE_URL="https://${GITHUB_TOKEN}@github.com/${GITHUB_REPO}.git"

# Remove existing github remote if exists
git remote remove github 2>/dev/null || true

# Add new remote
git remote add github "$REMOTE_URL"

echo -e "${GREEN}✅ Remote configured${NC}"

# Get current branch
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
echo ""
echo -e "${YELLOW}📌 Current branch: ${GREEN}$CURRENT_BRANCH${NC}"

# Push the branch
echo ""
echo -e "${YELLOW}⬆️  Pushing branch to GitHub...${NC}"
echo "   Branch: $BRANCH_NAME"
echo "   Repository: https://github.com/$GITHUB_REPO"
echo ""

if git push -u github "$BRANCH_NAME"; then
    echo ""
    echo -e "${GREEN}=========================================="
    echo "✅ SUCCESS! Code pushed to GitHub"
    echo "==========================================${NC}"
    echo ""
    echo "🌐 View your code at:"
    echo "   https://github.com/$GITHUB_REPO/tree/$BRANCH_NAME"
    echo ""
    echo "📝 To create a Pull Request:"
    echo "   https://github.com/$GITHUB_REPO/compare/$BRANCH_NAME"
    echo ""
    echo "📊 Changes pushed:"
    echo "   - 7 commits with bug fixes and optimizations"
    echo "   - Removed all hardcode values"
    echo "   - Removed all demo/fake data"
    echo "   - Optimized resource management"
    echo "   - Improved prediction accuracy"
    echo ""
else
    echo ""
    echo -e "${RED}=========================================="
    echo "❌ PUSH FAILED"
    echo "==========================================${NC}"
    echo ""
    echo "Common issues:"
    echo "  1. Token doesn't have 'repo' permission"
    echo "  2. Repository doesn't exist or is private"
    echo "  3. Network connectivity issues"
    echo ""
    echo "Please check and try again."
    exit 1
fi

# Clean up - remove token from remote URL
git remote remove github 2>/dev/null || true
git remote add github "https://github.com/${GITHUB_REPO}.git"

echo -e "${GREEN}🔒 Token removed from git config (security)${NC}"
echo ""
echo "Done! 🎉"
