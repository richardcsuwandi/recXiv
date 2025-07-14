#!/bin/bash

echo "🚀 Preparing RecXiv for Vercel deployment..."

# Copy Vercel-optimized requirements
echo "📦 Using Vercel-optimized requirements..."
cp requirements-vercel.txt requirements.txt

# Add and commit changes
echo "📝 Committing changes..."
git add .
git commit -m "Prepare for Vercel deployment" || echo "Nothing to commit"

# Push to GitHub
echo "⬆️  Pushing to GitHub..."
git push origin main || git push origin master

echo "✅ Repository prepared for Vercel deployment!"
echo ""
echo "Next steps:"
echo "1. Go to https://vercel.com/dashboard"
echo "2. Click 'New Project'"
echo "3. Import your GitHub repository"
echo "4. Vercel will automatically deploy using the configuration"
echo ""
echo "Or use Vercel CLI:"
echo "  npm i -g vercel"
echo "  vercel login"
echo "  vercel --prod" 