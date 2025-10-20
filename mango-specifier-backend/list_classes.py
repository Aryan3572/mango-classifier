import os

BASE_DIR = "dataset/train"
if not os.path.exists(BASE_DIR):
    raise SystemExit(f"Dataset folder not found: {BASE_DIR}")

classes = sorted([
    d for d in os.listdir(BASE_DIR)
    if os.path.isdir(os.path.join(BASE_DIR, d))
])

print("✅ Found classes:", classes)

for c in classes:
    class_path = os.path.join(BASE_DIR, c)
    num_images = sum(
        1 for f in os.listdir(class_path)
        if f.lower().endswith((".jpg", ".jpeg", ".png"))
    )
    print(f"  {c}: {num_images} images")
