#!/bin/bash
# Devin App Startup Guide
# This script shows how Devin should run the sports data analysis app

echo "🚀 DEVIN APP STARTUP GUIDE"
echo "=========================="
echo ""

echo "1. 📍 Navigate to project directory:"
echo "   cd ~/repos/devinai"
echo ""

echo "2. 🔧 Install dependencies (if needed):"
echo "   pip3 install --break-system-packages psutil aiohttp python-dotenv requests pytz"
echo ""

echo "3. 🚀 Start the main application:"
echo "   ./start.sh start"
echo ""

echo "4. 🔒 Start with SSH monitoring (recommended):"
echo "   ./start_ssh_monitor.sh"
echo ""

echo "5. ✅ Check application status:"
echo "   ./start.sh status"
echo ""

echo "6. 📊 Run comprehensive tests:"
echo "   python3 run_comprehensive_test.py"
echo ""

echo "7. 📝 View live logs:"
echo "   ./start.sh logs"
echo ""

echo "8. 🛑 Stop the application:"
echo "   ./start.sh stop"
echo ""

echo "🎯 KEY FILES DEVIN WILL SEE:"
echo "- step1.json: Live API data (12MB+)"
echo "- step2.json: Processed data (116KB)"
echo "- step7_simple.log: Filtered matches"
echo "- ssh_monitor.log: Network monitoring"
echo "- data_flow_analysis.json: Architecture analysis"
echo ""

echo "⚡ APPLICATION STATUS:"
echo "- Runs 24/7 with 60-second cycles"
echo "- Monitors 15+ SSH connections"
echo "- Tracks 138+ network connections"
echo "- Processes live sports data continuously"
echo ""

echo "=== DEVIN VS CODE INTEGRATION ==="
echo "VS Code profile export script downloaded and tested."
echo "Script location: ./devin_vscode_export.py"
echo "Status: Requires authentication (403 Forbidden when run standalone)"
echo "For manual setup: https://docs.devin.ai/collaborate-with-devin/vscode-profiles"
echo "Note: Project works independently of VS Code profile sync"
echo ""
