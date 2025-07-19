import requests
import time
import os
from faker import Faker

# Initialize Faker
fake = Faker()

# Endpoint of your deployed FastAPI app
URL = "https://cii-origin.onrender.com/generate-certificate"

# How many certificates to generate
TOTAL = 50

# Delay between requests (seconds)
DELAY = 1.5

# Folder to save PDFs
SAVE_FOLDER = "generated_pdfs"
os.makedirs(SAVE_FOLDER, exist_ok=True)

# Stats
success = 0
fail = 0
start_time = time.time()

for i in range(1, TOTAL + 1):
    print(f"\n🔄 Generating Origin PDF #{i}")

    data = {
        "exporter": fake.company(),
        "consignee": fake.company(),
        "pre_carriage_by": fake.word().capitalize(),
        "place_of_receipt": fake.city(),
        "vessel_flight_no": f"VF-{fake.random_number(digits=4)}",
        "port_of_loading": fake.city(),
        "lc_no": f"LC-{fake.random_number(digits=6)}",
        "port_of_discharge": fake.city(),
        "final_destination": fake.city(),
        "bl_awb_no": f"BL-{fake.random_number(digits=6)}",
        "marks_nosandcontainer_no": f"PKG-{fake.random_number(digits=3)}",
        "num_and_kind_of_pkgs": fake.word(),
        "description_of_goods": fake.sentence(),
        "quantity": str(fake.random_int(min=1, max=100)),
        "destination": fake.country(),
        "consignor": fake.name(),
        "invoice_number": f"INV-{fake.random_number(digits=4)}",
        "manufacturer": fake.company(),
        "nationality": fake.country(),
        "total_quantity": str(fake.random_int(min=100, max=1000)),
        "date": str(fake.future_date(end_date="+30d")),
        "exporter_signature": fake.name(),
        "certification_place": fake.city()
    }

    try:
        response = requests.post(URL, json=data)

        if response.status_code == 200:
            filename = os.path.join(SAVE_FOLDER, f"origin_{i}.pdf")
            with open(filename, "wb") as f:
                f.write(response.content)
            print(f"✅ {i}/{TOTAL} Success - Saved to {filename}")
            success += 1
        else:
            print(f"❌ {i}/{TOTAL} Failed: {response.status_code} - {response.text}")
            fail += 1

    except Exception as e:
        print(f"❌ {i}/{TOTAL} Error: {str(e)}")
        fail += 1

    time.sleep(DELAY)

end_time = time.time()
total_time = end_time - start_time
avg_time = total_time / TOTAL

print("\n📊 Performance Summary:")
print(f"🟢 Success: {success}")
print(f"🔴 Failed: {fail}")
print(f"⏱️ Total Time: {total_time:.2f} seconds")
print(f"⏱️ Avg Time per Request: {avg_time:.2f} seconds")
