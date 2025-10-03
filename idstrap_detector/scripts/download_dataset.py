"""Helper to download a Roboflow dataset into the project's data folder.

Usage:
    from scripts.download_dataset import download_dataset
    download_dataset()

This will read env vars if present, otherwise prompt for values.
"""
from pathlib import Path
import os
import shutil


def download_dataset(workspace=None, project=None, version=None, api_key=None, target_folder_name='ceit-id-lace'):
    """Download a YOLOv8 export from Roboflow into data/<target_folder_name>/.
    Returns the Path to the downloaded folder (data/<target_folder_name>/data.yaml) on success.
    """
    try:
        from roboflow import Roboflow
    except Exception as e:
        raise RuntimeError("roboflow package not installed. pip install roboflow") from e

    api_key = api_key or os.environ.get('ROBOFLOW_API_KEY')
    workspace = workspace or os.environ.get('ROBOFLOW_WORKSPACE')
    project = project or os.environ.get('ROBOFLOW_PROJECT')
    version = version or os.environ.get('ROBOFLOW_VERSION')

    if not api_key:
        api_key = input("Roboflow API key: ").strip()
    if not workspace:
        workspace = input("Roboflow workspace (e.g. jason-fml5e): ").strip()
    if not project:
        project = input("Roboflow project (e.g. ceit-id-lace): ").strip()
    if not version:
        version = input("Roboflow version (e.g. 1): ").strip()

    rf = Roboflow(api_key=api_key)
    proj = rf.workspace(workspace).project(project)
    ver = proj.version(int(version))

    data_parent = Path(__file__).parent.parent / 'data'
    data_parent.mkdir(parents=True, exist_ok=True)

    cwd = os.getcwd()
    try:
        # download into data_parent to keep things together
        os.chdir(str(data_parent))
        dataset = ver.download("yolov8")   # returns a Dataset object
        dl_folder = Path(dataset.location)  # ✅ FIX: use .location for actual path
    finally:
        os.chdir(cwd)

    # if download returned relative or other path, resolve
    if not dl_folder.exists():
        dl_folder = (data_parent / dl_folder).resolve()

    if not dl_folder.exists():
        raise RuntimeError(f"Downloaded folder not found: {dl_folder}")

    target = data_parent / target_folder_name
    # If target exists, merge contents
    if target.exists():
        print(f"Target folder {target} already exists; merging contents from {dl_folder}")
    else:
        target.mkdir(parents=True, exist_ok=True)

    # copy files from dl_folder into target (overwrite existing files)
    for item in dl_folder.iterdir():
        dest = target / item.name
        if item.is_dir():
            if dest.exists():
                # copy subcontent
                for sub in item.rglob('*'):
                    rel = sub.relative_to(item)
                    dest_sub = dest / rel
                    if sub.is_dir():
                        dest_sub.mkdir(parents=True, exist_ok=True)
                    else:
                        shutil.copy(sub, dest_sub)
            else:
                shutil.copytree(item, dest)
        else:
            shutil.copy(item, dest)

    data_yaml = target / 'data.yaml'
    if not data_yaml.exists():
        raise RuntimeError(f"Expected data.yaml in downloaded dataset at {target}, but not found")

    print(f"Downloaded dataset available at {target}")
    return data_yaml
