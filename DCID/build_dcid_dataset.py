import os
import random
from PIL import Image

def build_dcid_dataset(root, R, C, L, I, out_dir):
    """
    Build a resized and RWDA-augmented version of the Drill Core Image Dataset (DCID).

    Parameters:
    - root (str): Root directory that contains the original high-resolution folders
                  (e.g., 'DCID-512-7' and 'noise-512-7').
    - R (int): Target resolution for output images (e.g., 32, 64, 128, 256).
    - C (int): Number of lithology categories. Options: 7 or 35.
    - L (float): Real-world data augmentation (RWDA) level, i.e., proportion of defective samples to inject (0.0–0.4).
    - I (str): RWDA injection scope:
        - 'N' = None (no injection),
        - 'T' = Train set only,
        - 'E' = Test set only,
        - 'A' = All (both train and test sets).
    - out_dir (str): Output base directory to save the generated dataset.

    The original images (always read from 512×512 resolution) are resized to the target resolution R.
    Slightly defective samples are injected into the selected splits based on L and I parameters.

    Reference:
    Jia-Yu Li, Ji-Zhou Tang, Xian-Zheng Zhao, Bo Fan, Wen-Ya Jiang, Shun-Yao Song, Jian-Bing Li, Kai-Da Chen, Zheng-Guang Zhao.
    A large-scale, high-quality dataset for lithology identification: Construction and applications.
    Petroleum Science, 2025. ISSN 1995-8226.
    https://doi.org/10.1016/j.petsci.2025.04.013
    """

    assert I in {"N", "T", "E", "A"}, "I must be one of 'N', 'T', 'E', 'A'"
    assert C in {7, 35}, "C must be 7 or 35"

    orig_dir = os.path.join(root, f"DCID-512-{C}")       # Always use 512×512 as source
    noise_dir = os.path.join(root, f"noise-512-{C}")     # Defect source
    target_dir = os.path.join(out_dir, f"DCID-{R}-{C}-{L}-{I}")

    os.makedirs(target_dir, exist_ok=True)

    for split in ["train", "test"]:
        inject = (I == "A") or (I == "T" and split == "train") or (I == "E" and split == "test")
        print(f"Processing {split} set | inject defect: {inject}")

        split_orig_dir = os.path.join(orig_dir, split)
        split_noise_dir = os.path.join(noise_dir, split)

        for cls in os.listdir(split_orig_dir):
            orig_cls_path = os.path.join(split_orig_dir, cls)
            noise_cls_path = os.path.join(split_noise_dir, cls)
            out_cls_path = os.path.join(target_dir, split, cls)
            os.makedirs(out_cls_path, exist_ok=True)

            # Resize and copy original images
            for img_name in os.listdir(orig_cls_path):
                src_path = os.path.join(orig_cls_path, img_name)
                dst_path = os.path.join(out_cls_path, img_name)
                with Image.open(src_path) as im:
                    im = im.resize((R, R), Image.BILINEAR)
                    im.save(dst_path)

            # Inject defective images if applicable
            if inject:
                total = len(os.listdir(orig_cls_path))
                n_defect = int(L * total)
                defect_imgs = os.listdir(noise_cls_path)
                sampled = (
                    random.choices(defect_imgs, k=n_defect)
                    if n_defect > len(defect_imgs)
                    else random.sample(defect_imgs, k=n_defect)
                )

                for i, img_name in enumerate(sampled):
                    src_path = os.path.join(noise_cls_path, img_name)
                    dst_path = os.path.join(out_cls_path, f"defect_{i}_{img_name}")
                    with Image.open(src_path) as im:
                        im = im.resize((R, R), Image.BILINEAR)
                        im.save(dst_path)

        print(f"{split} set finished.\n")


# Example usage
build_dcid_dataset(
    root=".",         # Root directory containing DCID-512-7 and noise-512-7
    R=32,             # Output image resolution (e.g., 32×32)
    C=7,              # Number of lithology classes
    L=0.4,            # 40% RWDA level
    I="T",            # Inject defects into train set only
    out_dir="./output"
)
