#!/bin/bash
# Quick Kafka Stop Script

echo "🛑 Stopping Kafka..."
brew services stop kafka

echo ""
echo "✅ Kafka stopped."

echo ""
echo "🧹 Cleaning up Kafka data (optional)..."
echo "Kafka logs location: /opt/homebrew/var/lib/kafka-logs"
echo "To clean: rm -rf /opt/homebrew/var/lib/kafka-logs/*"
echo ""
echo "✅ Done!"
echo "✅ Kafka is stopped."