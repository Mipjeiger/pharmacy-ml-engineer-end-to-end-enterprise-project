#!/bin/bash
# Quick Kafka Start Script

echo "🚀 Starting Kafka..."
brew services start kafka

echo ""
echo "⏳ Waiting for Kafka to start (5 seconds)..."
sleep 5

echo ""
echo "📋 Creating topics..."

kafka-topics --create --topic pharmacy_bronze --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1
kafka-topics --create --topic pharmacy_silver --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1
kafka-topics --create --topic pharmacy_gold --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1

echo ""
echo "✅ Topics created! List of topics:"
kafka-topics --list --bootstrap-server localhost:9092

echo ""
echo "✅ Kafka is ready at localhost:9092"
