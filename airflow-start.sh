#!/bin/bash
# Start Airflow API Server, DAG Processor, and Scheduler

export AIRFLOW_HOME=$(pwd)/airflow

# Cleanup function to stop all services when exiting
cleanup() {
    echo ""
    echo "🛑 Stopping Airflow..."
    pkill -f "airflow api-server" 2>/dev/null
    pkill -f "airflow dag-processor" 2>/dev/null
    pkill -f "airflow scheduler" 2>/dev/null
    exit 0
}

# Trap Ctrl+C and call cleanup
trap cleanup SIGINT SIGTERM

echo "🚀 Starting Airflow..."
echo ""

# Kill any existing Airflow processes
pkill -f "airflow api-server" 2>/dev/null
pkill -f "airflow dag-processor" 2>/dev/null
pkill -f "airflow scheduler" 2>/dev/null
sleep 1

# Start API Server in background
echo "📡 Starting API Server on http://localhost:8080"
nohup airflow api-server > /tmp/airflow-api.log 2>&1 &
API_PID=$!

# Wait a bit
sleep 2

# Start DAG Processor in background (PENTING untuk Airflow 3.x!)
echo "🔄 Starting DAG Processor (parsing DAG files)"
nohup airflow dag-processor > /tmp/airflow-dag-processor.log 2>&1 &
DAG_PROC_PID=$!

# Wait a bit
sleep 2

# Start Scheduler in foreground
echo "⏰ Starting Scheduler (logs will appear below)"
echo "📊 Web UI: http://localhost:8080"
echo "📁 DAG Processor Log: /tmp/airflow-dag-processor.log"
echo "🛑 Press Ctrl+C to stop all services"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Run scheduler in foreground (this will show logs in terminal)
airflow scheduler
