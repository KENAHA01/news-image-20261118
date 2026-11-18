"""news-image-20261118 entry: copy the front page to the output dir.

Python 3.13, standard library only, no network, deterministic. The
program reads entry.png from its own directory and writes the same
bytes to $MAKEFUN_OUTPUT_DIR/entry.png (or /output/entry.png when
the variable is unset). The image itself is drawn by make_image.py,
which runs on the builder machine only.
"""

import os
import shutil
from pathlib import Path


def output_path():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    return Path(out_dir) / "entry.png"


def source_path():
    return Path(__file__).resolve().parent / "entry.png"


def main():
    src = source_path()
    if not src.is_file():
        raise FileNotFoundError(f"missing entry image beside main.py: {src}")
    dst = output_path()
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst)
    print(f"wrote {dst} ({dst.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
