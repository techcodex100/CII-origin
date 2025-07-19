import os
import time
import psutil
import requests
import pandas as pd

# === Settings ===
CSV_FILE = "origin_data_1.csv"  # Your CSV file
SAVE_FOLDER = "generated_origin_pdfs"  # Folder to save PDFs
ENDPOINT = "https://cii-origin.onrender.com/generate-origin-pdf/"  # API endpoint
MAX_PDFS = 30  # Limit the number of PDFs

# Ensure output folder exists
os.makedirs(SAVE_FOLDER, exist_ok=True)

def run_from_csv():
    print("🚀 Starting PDF generation from CSV...\n")

    # Load the CSV file
    try:
        df = pd.read_csv(CSV_FILE)
    except Exception as e:
        print(f"❌ Error reading CSV file '{CSV_FILE}': {e}")
        return

    total_rows = len(df)
    if total_rows == 0:
        print("⚠️ CSV is empty. Nothing to process.")
        return

    print(f"🔢 Total rows in CSV: {total_rows}")
    print(f"📌 Will process only the first {min(MAX_PDFS, total_rows)} rows.\n")

    confirm = input("⚠️ Continue with PDF generation (y/n)? ").strip().lower()
    if confirm != 'y':
        print("❌ Operation cancelled by user.")
        return

    start_time = time.time()
    success_count = 0

    for idx, row in df.head(MAX_PDFS).iterrows():
        print(f"\n📤 Generating PDF #{idx + 1}...")

        try:
            # Convert row to dictionary, ensuring all values are strings
            data = row.dropna().astype(str).to_dict()

            response = requests.post(ENDPOINT, json=data, timeout=60)
            content_type = response.headers.get("content-type", "")

            if response.status_code == 200 and "application/pdf" in content_type:
                filename = f"origin_certificate_{idx + 1}.pdf"
                file_path = os.path.join(SAVE_FOLDER, filename)
                with open(file_path, "wb") as f:
                    f.write(response.content)
                print(f"✅ Saved: {filename}")
                success_count += 1
            else:
                print(f"❌ Failed PDF #{idx + 1} - Status: {response.status_code}")
                print(f"📝 Response: {response.text}")

        except Exception as e:
            print(f"💥 Error while processing row #{idx + 1}: {e}")

        time.sleep(2.0)  # Delay between requests

    print_stats(start_time, success_count)

def print_stats(start_time, success_count):
    end_time = time.time()
    duration = round(end_time - start_time, 2)
    mem_usage = psutil.Process().memory_info().rss / 1024 / 1024  # in MB
    cpu = psutil.cpu_percent(interval=1)

    print("\n📊 Summary Report:")
    print(f"✅ Total PDFs Generated: {success_count}")
    print(f"⏱️ Time Taken: {duration} seconds")
    print(f"🧠 Memory Used: {mem_usage:.2f} MB")
    print(f"⚙️ CPU Usage: {cpu}%")

if __name__ == "__main__":
    run_from_csv()
