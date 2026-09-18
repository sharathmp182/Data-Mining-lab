import os

base = r"lake\sales"
target = r"lake\sales\year=2024\month=3\store_id=S05"

def get_stats(folder):
    files = []
    total_bytes = 0

    for root, dirs, filenames in os.walk(folder):
        for name in filenames:
            path = os.path.join(root, name)
            files.append(path)
            total_bytes += os.path.getsize(path)

    return len(files), total_bytes

all_files, all_bytes = get_stats(base)
target_files, target_bytes = get_stats(target)

print("ENTIRE DATASET")
print("Files :", all_files)
print("Bytes :", all_bytes)

print("\nMARCH 2024 - STORE S05")
print("Files :", target_files)
print("Bytes :", target_bytes)

print("\nREDUCTION")
print("File reduction :", round((1 - target_files / all_files) * 100, 2), "%")
print("Byte reduction :", round((1 - target_bytes / all_bytes) * 100, 2), "%")