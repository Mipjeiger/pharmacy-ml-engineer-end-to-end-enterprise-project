#!/bin/bash
# Start all Airflow services in background (untuk testing)

export AIRFLOW_HOME=$(pwd)/airflow

echo "🚀 Starting Airflow (all services in background)..."
echo ""

# Kill any existing Airflow processes
pkill -f "airflow api-server" 2>/dev/null
pkill -f "airflow dag-processor" 2>/dev/null
pkill -f "airflow scheduler" 2>/dev/null
sleep 1

# Start API Server
echo "📡 Starting API Server on http://localhost:8080"
nohup airflow api-server > /tmp/airflow-api.log 2>&1 &

sleep 2

# Start DAG Processor (PENTING untuk Airflow 3.x!)
echo "🔄 Starting DAG Processor"
nohup airflow dag-processor > /tmp/airflow-dag-processor.log 2>&1 &

sleep 2

# Start Scheduler
echo "⏰ Starting Scheduler"
nohup airflow scheduler > /tmp/airflow-scheduler.log 2>&1 &

sleep 3

echo ""
echo "✅ Airflow services started!"
echo "📊 Web UI: http://localhost:8080"
echo "📝 Logs:"
echo "   - API Server: /tmp/airflow-api.log"
echo "   - DAG Processor: /tmp/airflow-dag-processor.log"
echo "   - Scheduler: /tmp/airflow-scheduler.log"
echo ""
echo "🔍 Check processes:"
ps aux | grep -E "airflow (api-server|dag-processor|scheduler)" | grep -v grep
echo ""
echo "🛑 To stop: ./airflow-stop.sh"
