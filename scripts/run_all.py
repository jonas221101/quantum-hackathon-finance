"""Entry point: python scripts/run_all.py run [--fast] [--canonical] [--set key=value] | diff <runA> <runB>."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from qhf.cli import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
