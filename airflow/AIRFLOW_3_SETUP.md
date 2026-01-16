# Airflow 3.x Setup Guide

## Masalah yang Ditemukan

Pada Airflow 3.x terdapat **perubahan arsitektur besar** dimana **DAG Processor harus dijalankan sebagai service terpisah**.

### Gejala Masalah
- DAG tidak muncul di UI (No Dag Runs found)
- `airflow dags list` menampilkan "No data found"
- Scheduler berjalan tapi tidak parsing DAG files
- Tidak ada log "Parsing DAG files" atau "Added DAG" di scheduler

### Root Cause
Di Airflow 3.x, proses parsing DAG files dipindahkan ke service terpisah bernama **`dag-processor`**. Jika hanya menjalankan `scheduler` saja, DAG tidak akan pernah di-parse.

## Solusi

### 1. Menjalankan Airflow 3.x dengan DAG Processor

Anda **HARUS** menjalankan 3 service:
1. **API Server** - untuk Web UI
2. **DAG Processor** - untuk parsing DAG files
3. **Scheduler** - untuk scheduling tasks

```bash
# Gunakan script yang sudah diperbaiki
./airflow-start.sh
```

Script akan menjalankan:
```bash
airflow api-server      # Background
airflow dag-processor   # Background  
airflow scheduler       # Foreground (logs visible)
```

### 2. Konfigurasi yang Diperbaiki

#### `airflow.cfg`
```ini
# Nonaktifkan safe mode agar lebih fleksibel (opsional)
dag_discovery_safe_mode = False

# Percepat interval scanning (10 detik vs default 30 detik)
min_file_process_interval = 10
```

### 3. Verifikasi Setup

```bash
# Cek apakah semua service berjalan
ps aux | grep airflow | grep -v grep

# Cek log dag-processor
tail -f /tmp/airflow-dag-processor.log

# Cek DAG terdeteksi
export AIRFLOW_HOME=/path/to/airflow
airflow dags list
```

### 4. Stop All Services

```bash
./airflow-stop.sh
```

## Log Locations

- **API Server**: `/tmp/airflow-api.log`
- **DAG Processor**: `/tmp/airflow-dag-processor.log`
- **Scheduler**: Tampil di terminal (foreground)

## Referensi Breaking Changes Airflow 3.x

1. **webserver** → **api-server**
2. **db init** → **db migrate**
3. **schedule_interval** → **schedule**
4. DAG Processor sekarang **service terpisah**
5. Banyak config dipindah dari `[webserver]` ke `[api]`

## Troubleshooting

### DAG masih tidak muncul setelah menjalankan dag-processor?
```bash
# Cek log dag-processor untuk error
tail -100 /tmp/airflow-dag-processor.log

# Cek import error
airflow dags list-import-errors

# Test import manual
cd /path/to/airflow/dags
python -c "from pharmacy_streaming_pipeline import dag; print(dag)"
```

### Error "No module named 'airflow.providers.standard'"?
```bash
# Install provider package
pip install apache-airflow-providers-standard
```
