import sys
import os

current_dir = os.getcwd()
sys.path.insert(0, current_dir)

print(f"Current directory: {current_dir}")
print(f"Folders in current directory: {os.listdir()}")

try:
    from customer_ingestion.src.ingestion_service import DataIngestionService
    print("✅ Import successful!")
except Exception as e:
    print(f"❌ Import failed: {e}")