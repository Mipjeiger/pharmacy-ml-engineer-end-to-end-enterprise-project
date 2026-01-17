# Summary: Data MinIO - Timestamp vs Upload Time

## 📊 Hasil Investigasi

### ❌ Masalah yang Ditemukan:
- **Tidak ada file baru yang dibuat hari ini (17 Januari 2026)**
- Semua file di MinIO memiliki `last_modified` dari **16 Januari 2026**
- DAG run terbaru (17 Jan 12:04 PM) **SUCCESS** tapi **tidak menambahkan file baru**

### 🔍 Root Cause Analysis:

#### 1. **Pipeline Flow:**
```
DB → bronze_ingestion → Kafka TOPIC_BRONZE → save_bronze_to_minio → MinIO
```

#### 2. **Kafka Consumer Behavior:**
- `save_to_minio()` menggunakan `earliest=True` 
- Artinya: **Consume dari awal topic**
- Tapi jika consumer sudah pernah jalan dengan `group_id` yang sama, akan **resume dari last offset**

#### 3. **Filename Timestamp:**
- File `bronze/20260116_225008.json` = Timestamp saat `write_json()` dipanggil
- Timestamp dibuat oleh function ini (di `minio_utils.py`):
```python
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f"{timestamp}.json"
```

### ✅ Kesimpulan:

**File-file tersebut SEBENARNYA sudah ada dari kemarin!**

Saat DAG run hari ini:
1. ✅ `bronze_ingestion` → Push data ke Kafka (SUCCESS)
2. ✅ `silver_transformation` → Transform data (SUCCESS)  
3. ✅ `gold_aggregation` → Aggregate data (SUCCESS)
4. ✅ `save_to_minio` → **SKIP** (karena tidak ada messages baru atau consumer offset sudah di akhir)

### 🎯 Solusi:

Ada 3 cara untuk memastikan data BARU masuk ke MinIO:

#### **Option 1: Change Consumer Group ID** (RECOMMENDED)
Ubah `group_id` di DAG agar consumer mulai dari awal:

```python
def save_to_minio(topic, prefix, max_messages=2000):
    # Generate unique group_id setiap run
    import uuid
    unique_group = f"airflow-minio-{prefix}-{uuid.uuid4().hex[:8]}"
    
    consumer = get_kafka_consumer(
        topic=topic,
        group_id=unique_group,  # Unique ID = start from beginning
        earliest=True,
    )
    # ...
```

#### **Option 2: Delete MinIO Files & Re-run**
Hapus semua file di MinIO, lalu trigger DAG:

```bash
# Via MinIO Console: http://localhost:9011
# Delete all objects in pharmacy-data bucket
```

#### **Option 3: Check Kafka Topics**
Lihat apakah masih ada messages di Kafka:

```bash
# List Kafka topics
kafka-topics --bootstrap-server localhost:9092 --list

# Check messages in topic
kafka-console-consumer --bootstrap-server localhost:9092 \
  --topic pharmacy-bronze --from-beginning --max-messages 5
```

### 📝 Rekomendasi:

**Untuk production:** Gunakan **unique consumer group ID** atau **timestamp-based group ID** agar setiap DAG run consume data terbaru.

**Untuk development:** Anda bisa:
1. Hapus file lama di MinIO
2. Reset Kafka consumer offset
3. Re-run DAG untuk generate file baru dengan timestamp hari ini

## 🔄 Next Steps:

Jika Anda ingin file dengan timestamp **hari ini (17 Jan)**, Anda perlu:

1. **Hapus file lama** di MinIO (atau pindahkan ke folder archive)
2. **Trigger DAG** dengan consumer group baru
3. File baru akan dibuat dengan timestamp `20260117_xxx`

Atau terima bahwa file tersebut sudah **represent data terbaru** dari database, hanya timestampnya dari kemarin saat pertama kali dibuat.
