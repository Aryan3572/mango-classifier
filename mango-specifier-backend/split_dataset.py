# split_dataset.py
import os
import random
import shutil

src = "Image dataset (2)/Image dataset"
dst = "dataset"  # will create dataset/train, dataset/val, dataset/test
ratios = (0.7, 0.15, 0.15)
seed = 123

random.seed(seed)
os.makedirs(dst, exist_ok=True)

for cls in sorted(os.listdir(src)):
    cls_path = os.path.join(src, cls)
    if not os.path.isdir(cls_path):
        continue
    imgs = [f for f in os.listdir(cls_path) if f.lower().endswith((".jpg"))]
    random.shuffle(imgs)
    n = len(imgs)
    n1 = int(n * ratios[0])
    n2 = n1 + int(n * ratios[1])
    splits = {
        'train': imgs[:n1],
        'val': imgs[n1:n2],
        'test': imgs[n2:]
    }
    for split, files in splits.items():
        outdir = os.path.join(dst, split, cls)
        os.makedirs(outdir, exist_ok=True)
        for f in files:
            shutil.copy2(os.path.join(cls_path, f), os.path.join(outdir, f))

print("Split complete. Check dataset/train, dataset/val, dataset/test")
