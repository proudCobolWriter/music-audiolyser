from pathlib import Path

TF_ROOT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT_DIR = TF_ROOT_DIR.parent.parent.parent

def path_to_str(pathlike: Path, absolute: bool = False, relative_from: Path = TF_ROOT_DIR) -> str:
    if absolute:
        return str(pathlike.absolute())
    return str(pathlike.relative_to(relative_from))
