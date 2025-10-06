# list_classes.py
import os

base = "Image dataset (2)/Image dataset"
if not os.path.exists(base):
    raise SystemExit(
        f"{base} not found. Put images under Image dataset(2)/Image dataset"
    )

classes = sorted([
    d for d in os.listdir(base)
    if os.path.isdir(os.path.join(base, d))
])
print("Found classes:", classes)
for c in classes:
    p = os.path.join(base, c)
    n = sum(1 for f in os.listdir(p) if f.lower().endswith((".jpg")))
    print(f"  {c}: {n} images")
