"""
DCID-35 岩相分類 学習スクリプト (EfficientNet-B4 / timm / PyTorch)

使い方:
  # 動作確認（各クラス50枚だけ・1エポック）
  python train_dcid35.py --limit-per-class 50 --epochs 1

  # 本番
  python train_dcid35.py --epochs 30

設計方針:
  - train を train/val に層化分割し、val でモデル選択する。
    test は最後に1回だけ評価する（test でベスト選択すると test に過適合するため）。
  - 依存を増やさない（albumentations/opencv/sklearn は使わない）。
    DLLブロック(Smart App Control)の発生源を減らすため。
  - augmentation は色相を変えない（色が岩相の手がかりになるため）。
"""
import argparse
import json
import random
import time
from pathlib import Path

import numpy as np
import timm
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Subset
from torchvision import datasets, transforms



#実行時のパラメーター
def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--data", default=r"DCID/DCID-512-35")
    p.add_argument("--out", default="output")
    #解像度
    p.add_argument("--img", type=int, default=384, help="入力解像度(元は512)")
    #バッチサイズ
    p.add_argument("--bs", type=int, default=16)
    p.add_argument("--epochs", type=int, default=30)
    #学習率
    p.add_argument("--lr", type=float, default=3e-4)
    #重み減衰（重みが過大になるのを防いで，過学習を防止）
    p.add_argument("--wd", type=float, default=1e-2)
    p.add_argument("--val-frac", type=float, default=0.1)
    p.add_argument("--workers", type=int, default=4)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--limit-per-class", type=int, default=0, help="動作確認用。0なら全件")
    p.add_argument("--no-pretrained", action="store_true")
    return p.parse_args()


def set_seed(seed):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


def stratified_split(targets, val_frac, seed, limit_per_class=0):
    rng = random.Random(seed)
    by_class = {}
    for i, t in enumerate(targets):
        by_class.setdefault(t, []).append(i)
    train_idx, val_idx = [], []
    for t, idxs in by_class.items():
        rng.shuffle(idxs)
        if limit_per_class > 0:
            idxs = idxs[:limit_per_class]
        n_val = max(1, int(len(idxs) * val_frac))
        val_idx += idxs[:n_val]
        train_idx += idxs[n_val:]
    return train_idx, val_idx


@torch.no_grad()
def evaluate(model, loader, device, criterion):
    model.eval()
    total_loss, correct, n = 0.0, 0, 0
    all_pred, all_true = [], []
    for x, y in loader:
        x, y = x.to(device, non_blocking=True), y.to(device, non_blocking=True)
        with torch.autocast(device_type="cuda", dtype=torch.float16):
            logits = model(x)
            loss = criterion(logits, y)
        total_loss += loss.item() * x.size(0)
        pred = logits.argmax(1)
        correct += (pred == y).sum().item()
        n += x.size(0)
        all_pred.append(pred.cpu())
        all_true.append(y.cpu())
    return total_loss / n, correct / n, torch.cat(all_pred).numpy(), torch.cat(all_true).numpy()


def main():
    args = parse_args()
    set_seed(args.seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if device.type != "cuda":
        raise SystemExit("CUDAが使えません。torchがCPU版の可能性があります。")
    print(f"device: {torch.cuda.get_device_name(0)}  torch {torch.__version__}")

    data_root = Path(args.data)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    mean, std = (0.485, 0.456, 0.406), (0.229, 0.224, 0.225)
    #ランダムな画像処理
    train_tf = transforms.Compose([
        transforms.Resize((args.img, args.img)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomVerticalFlip(),
        transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.1),  # hueは触らない
        transforms.ToTensor(),
        transforms.Normalize(mean, std),
    ])
    #最低限の画像処理
    eval_tf = transforms.Compose([
        transforms.Resize((args.img, args.img)),
        transforms.ToTensor(),
        transforms.Normalize(mean, std),
    ])

    # 同じフォルダを前処理だけ変えて2回読む
    full_train = datasets.ImageFolder(data_root / "train", transform=train_tf)
    full_eval = datasets.ImageFolder(data_root / "train", transform=eval_tf)
    test_set = datasets.ImageFolder(data_root / "test", transform=eval_tf)
    assert full_train.class_to_idx == test_set.class_to_idx, "train/testでクラス対応が不一致"

    classes = full_train.classes
    num_classes = len(classes)

    print(f"classes: {num_classes}")

    train_idx, val_idx = stratified_split(
        full_train.targets, args.val_frac, args.seed, args.limit_per_class)
    train_set = Subset(full_train, train_idx)
    val_set = Subset(full_eval, val_idx)
    if args.limit_per_class > 0:
        # 動作確認時はtestも間引く
        _, t_idx = stratified_split(test_set.targets, 1.0, args.seed, args.limit_per_class)
        test_set = Subset(test_set, t_idx)
    print(f"train {len(train_set)} / val {len(val_set)} / test {len(test_set)}")

    kw = dict(num_workers=args.workers, pin_memory=True,
              persistent_workers=args.workers > 0)
    #画像を16枚まとめてっモデルに渡す．
    train_loader = DataLoader(train_set, batch_size=args.bs, shuffle=True, drop_last=True, **kw)
    val_loader = DataLoader(val_set, batch_size=args.bs * 2, shuffle=False, **kw)
    test_loader = DataLoader(test_set, batch_size=args.bs * 2, shuffle=False, **kw)


    model = timm.create_model(
        "efficientnet_b4", pretrained=not args.no_pretrained, num_classes=num_classes
    ).to(device)

    criterion = nn.CrossEntropyLoss(label_smoothing=0.1)
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=args.wd)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=args.epochs)
    scaler = torch.cuda.amp.GradScaler()

    best_val, history = 0.0, []
    ckpt_path = out_dir / "best_model.pth"


    #学習ループ
    for epoch in range(1, args.epochs + 1):
        model.train()
        t0 = time.time()
        run_loss, run_correct, run_n = 0.0, 0, 0
        for x, y in train_loader:
            x, y = x.to(device, non_blocking=True), y.to(device, non_blocking=True)
            optimizer.zero_grad(set_to_none=True)
            with torch.autocast(device_type="cuda", dtype=torch.float16):
                logits = model(x)
                loss = criterion(logits, y)
            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()
            run_loss += loss.item() * x.size(0)
            run_correct += (logits.argmax(1) == y).sum().item()
            run_n += x.size(0)
        scheduler.step()

        val_loss, val_acc, _, _ = evaluate(model, val_loader, device, criterion)
        rec = dict(epoch=epoch, train_loss=run_loss / run_n, train_acc=run_correct / run_n,
                   val_loss=val_loss, val_acc=val_acc, sec=time.time() - t0)
        history.append(rec)
        print(f"[{epoch:02d}/{args.epochs}] train loss {rec['train_loss']:.3f} acc {rec['train_acc']:.3f} | "
              f"val loss {val_loss:.3f} acc {val_acc:.3f} | {rec['sec']:.0f}s")

        if val_acc > best_val:
            best_val = val_acc
            torch.save({
                "model_state": model.state_dict(),
                "class_to_idx": full_train.class_to_idx,  # 推論時に必須
                "classes": classes,
                "img_size": args.img,
                "arch": "efficientnet_b4",
                "val_acc": val_acc,
                "epoch": epoch,
                "args": vars(args),
            }, ckpt_path)


    with open(out_dir / "history.json", "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

    # ---- 最終評価: testは1回だけ ----
    print("\n=== best checkpoint を test で評価 ===")
    ckpt = torch.load(ckpt_path, map_location=device)
    model.load_state_dict(ckpt["model_state"])
    test_loss, test_acc, pred, true = evaluate(model, test_loader, device, criterion)
    print(f"best val acc {ckpt['val_acc']:.4f} (epoch {ckpt['epoch']}) / test acc {test_acc:.4f}")

    cm = np.zeros((num_classes, num_classes), dtype=np.int64)
    for t, p_ in zip(true, pred):
        cm[t, p_] += 1
    np.savetxt(out_dir / "confusion_matrix.csv", cm, fmt="%d", delimiter=",",
               header=",".join(classes), comments="")

    per_class = cm.diagonal() / np.maximum(cm.sum(1), 1)
    print("\n--- クラス別 test 精度（低い順） ---")
    for i in np.argsort(per_class):
        print(f"  {per_class[i]:.3f}  {classes[i]}")

    off = cm.copy()
    np.fill_diagonal(off, 0)
    print("\n--- 混同の多いペア Top10 (正解 -> 予測) ---")
    for flat in np.argsort(off, axis=None)[::-1][:10]:
        i, j = divmod(int(flat), num_classes)
        if off[i, j] == 0:
            break
        print(f"  {off[i, j]:4d}  {classes[i]}  ->  {classes[j]}")


if __name__ == "__main__":  # Windowsのmultiprocessingに必須
    main()
    print("ざーこ")