import os
import shutil
import yaml
from pathlib import Path
from ultralytics import YOLO
from .config import DATASET_PATH, WEIGHTS_DIR, BEST_WEIGHTS

# config may export paths as strings; ensure we have Path objects here
WEIGHTS_DIR = Path(WEIGHTS_DIR)
BEST_WEIGHTS = Path(BEST_WEIGHTS)


def _resolve_data_yaml(src_yaml: Path) -> Path:
    """Read a data.yaml, resolve relative paths (train/val/test) to absolute paths
    based on the yaml's parent directory, and write a temporary yaml file returning its path.
    """
    src_yaml = Path(src_yaml)
    if not src_yaml.exists():
        raise FileNotFoundError(f"data.yaml not found at {src_yaml}")

    with open(src_yaml, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)

    base = src_yaml.parent
    for key in ('train', 'val', 'test'):
        if key in data and data[key] is not None and not os.path.isabs(str(data[key])):
            data[key] = str((base / data[key]).resolve())

    # If `path` is present and is '.' or relative, convert it too
    if 'path' in data and (data['path'] == '.' or not os.path.isabs(str(data['path']))):
        data['path'] = str(base.resolve())

    tmp = src_yaml.parent / 'data_resolved_tmp.yaml'
    with open(tmp, 'w', encoding='utf-8') as f:
        yaml.safe_dump(data, f)
    return tmp


def train(epochs=30, batch=16, imgsz=640):
    """Train YOLO model using ultralytics on DATASET_PATH (data.yaml).
    This resolves relative paths inside data.yaml so Ultralytics finds images.
    After training, copy runs/.../weights/best.pt to models/best.pt if present.
    """
    WEIGHTS_DIR.mkdir(parents=True, exist_ok=True)
    print(f"[TRAIN] Dataset: {DATASET_PATH}")

    resolved_yaml = _resolve_data_yaml(Path(DATASET_PATH))
    print(f"[TRAIN] Using resolved data.yaml at: {resolved_yaml}")

    # check that train/val/test folders actually contain images
    import yaml as _yaml
    with open(resolved_yaml, 'r', encoding='utf-8') as f:
        data_map = _yaml.safe_load(f)

    train_path = Path(data_map.get('train', ''))
    val_path = Path(data_map.get('val', ''))

    def _has_images(p: Path) -> bool:
        try:
            exts = ['jpg', 'jpeg', 'png', 'bmp', 'webp', 'tif', 'tiff']
            for ext in exts:
                # any() over the rglob generator will be True if at least one file matches
                if any(p.rglob(f"*.{ext}")):
                    return True
            return False
        except Exception:
            return False

    if not train_path.exists() or not _has_images(train_path):
        print(f"[WARN] No training images found in {train_path}")
        # attempt Roboflow download interactively or via env vars
        try:
            from scripts.download_dataset import download_dataset
        except Exception:
            download_dataset = None

        ask = None
        if download_dataset is not None:
            # interactive prompt
            try:
                ask = input("No training images found. Would you like to download dataset from Roboflow now? [y/N]: ").strip().lower()
            except Exception:
                ask = 'n'

        if ask == 'y' and download_dataset is not None:
            # call helper (it will prompt for missing values)
            data_yaml = download_dataset()
            resolved_yaml = _resolve_data_yaml(data_yaml)
            print(f"[INFO] Dataset downloaded and resolved at {resolved_yaml}")
        else:
            # fallback: try environment variables (non-interactive)
            rf_key = os.environ.get('ROBOFLOW_API_KEY')
            rf_ws = os.environ.get('ROBOFLOW_WORKSPACE')
            rf_proj = os.environ.get('ROBOFLOW_PROJECT')
            rf_ver = os.environ.get('ROBOFLOW_VERSION')
            if rf_key and rf_ws and rf_proj and rf_ver:
                print("[INFO] ROBOFLOW env vars found: attempting to download dataset from Roboflow...")
                try:
                    data_parent = Path(DATASET_PATH).parent.parent
                    # reuse helper if present
                    if download_dataset is not None:
                        data_yaml = download_dataset(rf_ws, rf_proj, rf_ver, rf_key)
                    else:
                        # minimal fallback: use Roboflow client directly
                        from roboflow import Roboflow
                        rf = Roboflow(api_key=rf_key)
                        project = rf.workspace(rf_ws).project(rf_proj)
                        version = project.version(int(rf_ver))
                        cwd = os.getcwd()
                        try:
                            os.chdir(str(data_parent))
                            dl = version.download("yolov8")
                        finally:
                            os.chdir(cwd)
                        # find downloaded folder
                        found = None
                        for p in data_parent.iterdir():
                            if p.is_dir() and (p / 'data.yaml').exists():
                                found = p
                                break
                        if found:
                            data_yaml = found / 'data.yaml'
                        else:
                            raise RuntimeError("Roboflow download completed but data.yaml not found")

                    resolved_yaml = _resolve_data_yaml(data_yaml)
                    print(f"[INFO] Dataset downloaded and resolved at {resolved_yaml}")
                except Exception as e:
                    raise RuntimeError(f"Failed to download dataset from Roboflow: {e}") from e
            else:
                raise FileNotFoundError(
                    f"Training images not found under {train_path}.\n" \
                    "Place your Roboflow-exported dataset under data/ceit-id-lace/ (with train/ valid/ test folders),\n" \
                    "or set environment variables ROBOFLOW_API_KEY, ROBOFLOW_WORKSPACE, ROBOFLOW_PROJECT, ROBOFLOW_VERSION to download automatically."
                )

    model = YOLO("yolov8n.pt")
    model.train(data=str(resolved_yaml), epochs=epochs, batch=batch, imgsz=imgsz, name="idstrap_exp")

    run_dir = Path("runs") / "detect" / "idstrap_exp"
    best = run_dir / "weights" / "best.pt"
    if best.exists():
        dest = BEST_WEIGHTS
        shutil.copy(best, dest)
        print(f"[TRAIN] Best model copied to {dest}")
    else:
        print("[TRAIN] Training finished but best.pt not found at expected path.")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--epochs", type=int, default=20)
    parser.add_argument("--batch", type=int, default=8)
    parser.add_argument("--imgsz", type=int, default=640)
    args = parser.parse_args()
    train(epochs=args.epochs, batch=args.batch, imgsz=args.imgsz)
