import os
import json
import pandas as pd

# ==== Paths ====
json_dir = r"D:\crosspl\PolyBench\IPC_Bench\c++_ipc"
csv_path = r"D:\crosspl\RepositoryList.csv"
save_dir = r"D:\crosspl\PolyBench\IPC_Bench\year\c++"

# Create output directory if not exists
if not os.path.exists(save_dir):
    os.makedirs(save_dir)

# ==== Load CSV ====
df = pd.read_csv(csv_path)

# Ensure required columns exist
if not {"Id", "Pushed", "Created"}.issubset(df.columns):
    raise ValueError("CSV file must contain 'Id', 'Pushed', and 'Created' columns.")

# Build lookup: Id -> Year
id_to_year = {}

for _, row in df.iterrows():
    repo_id = str(row["Id"])

    pushed = row["Pushed"]
    created = row["Created"]

    # Use Pushed if not empty, else Created
    timestamp = None

    if pd.notna(pushed) and str(pushed).strip() != "":
        timestamp = str(pushed)
    elif pd.notna(created) and str(created).strip() != "":
        timestamp = str(created)

    # Extract year
    year = timestamp[:4] if timestamp and len(timestamp) >= 4 else None

    id_to_year[repo_id] = year

# ==== Process JSON files ====
for filename in os.listdir(json_dir):
    if not filename.lower().endswith(".json"):
        continue

    json_path = os.path.join(json_dir, filename)

    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        github_id = str(data.get("Github_ID", None))
        if github_id is None:
            print(f"Warning: File {filename} has no Github_ID. Skipped.")
            continue

        year = id_to_year.get(github_id, None)
        if year is None:
            print(f"Warning: No valid timestamp for Github_ID={github_id}. File {filename} skipped.")
            continue

        # Add new field
        data["Year"] = year

        # Save updated JSON
        save_path = os.path.join(save_dir, filename)
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        print(f"Processed: {filename}  →  Year={year}")

    except Exception as e:
        print(f"Error processing {filename}: {e}")

print("All JSON files processed successfully.")
