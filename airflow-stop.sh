#!/bin/bash
# Stop all Airflow services

echo "🛑 Stopping Airflow..."

# Kill all Airflow processes
pkill -f "airflow api-server" 2>/dev/null
pkill -f "airflow dag-processor" 2>/dev/null
pkill -f "airflow scheduler" 2>/dev/null

sleep 1

echo "✅ Airflow stopped!"
echo ""
echo "Remaining processes:"
ps aux | grep airflow | grep -v grep
