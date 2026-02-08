#!/bin/bash
# Build and deploy to GitHub Pages
# Run from the archive-app directory

npm run build

# Copy built files to docs/ in repo root (GitHub Pages serves from /docs)
rm -rf ../docs
cp -r dist ../docs

echo "Built and copied to ../docs — commit and push to deploy."
