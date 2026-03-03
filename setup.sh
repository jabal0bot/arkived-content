#!/bin/bash
# Setup script for Arkived Content Pipeline

echo "Setting up MTH240 pipeline..."

# Create directories
mkdir -p uploads/MTH240
mkdir -p courses/MTH240/{raw,processing,finished/{midterms,finals,content}}

echo "Directories created"
echo ""
echo "To process upload:"
echo "  python courses/MTH240/scripts/process_upload.py --zip uploads/MTH240/your_file.zip"
echo ""
echo "Or manually:"
echo "  1. Drop zip in uploads/MTH240/"
echo "  2. Run: python courses/MTH240/scripts/process_upload.py --zip <file>"
echo "  3. Agent will enrich questions from processing/"
