#!/usr/bin/env python3
"""
Wild‑Gaussians Runner (간소화 버전)
──────────────────────────────────
* **trajectory** 파일이 없어도 동작하도록 렌더 단계는 **옵션**으로 변경했습니다.
* 출력 경로는 각 CONFIG 항목의 `output` 값이 우선이며, 없으면
  `DEFAULT_OUT_ROOT/SELECT/`에 저장됩니다.
* 더 이상 `--out_root` CLI 옵션은 제공하지 않습니다 ─ 필요하면 CONFIG만 고쳐서 사용하세요.

예시
────
# CONFIG 에 정의된 trevi 항목 학습
python exe_wg.py --select trevi
"""
import argparse
import subprocess
import sys
from pathlib import Path
from typing import Dict

# ─────────────────────────────────────
# 데이터셋 설정
# ─────────────────────────────────────
CONFIG: Dict[str, Dict] = {
    "trevi": {
        "method": "wild-gaussians",
        "data": "datasets/phototourism/trevi-fountain",
        "output": "outputs/trevi",
        # "trajectory": "trajectories/trevi.json",  # 렌더링이 필요하면 주석 해제
    },
    "custom": {
        "method": "wild-gaussians",
        "data": "/path/to/your/dataset",  # 수정하세요
        # "output": "outputs/custom",
        # "trajectory": "trajectories/custom.json",
    },
    "sculpture": {
        "method": "wild-gaussians",
        "data": "datasets/dronesplat-dataset/Sculpture/dense",
        "output": "outputs/drone-sculpture",
    },
}

# @@@@@@@@@@@@@@@@@@@@@@@@@@
# @@@@@    아래 수정     @@@@@
# @@@@@@@@@@@@@@@@@@@@@@@@@@
DEFAULT_SELECT = "sculpture"


DEFAULT_OUT_ROOT = "outputs"  # select 하위 폴더까지 자동 결합됨

# ─────────────────────────────────────
# 헬퍼
# ─────────────────────────────────────

def sh(cmd: str):
    print(f"\n$ {cmd}")
    subprocess.run(cmd, shell=True, check=True)


def ensure_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)


def resolve_out_dir(select: str):
    cfg_out = CONFIG[select].get("output")
    return Path(cfg_out) if cfg_out else Path(DEFAULT_OUT_ROOT) / select


# ─────────────────────────────────────
# 메인
# ─────────────────────────────────────

def parse_args():
    p = argparse.ArgumentParser(description="Wild‑Gaussians runner (simple)")
    p.add_argument("--select", choices=CONFIG.keys(), default=DEFAULT_SELECT,
                   help="dataset key (default: %(default)s)")
    return p.parse_args()


def main():
    args = parse_args()
    cfg = CONFIG[args.select]

    out_dir = resolve_out_dir(args.select)
    chk = out_dir / "checkpoint.ckpt"
    ensure_dir(out_dir)

    # 1. Training
    sh(
        f"nerfbaselines train --method {cfg['method']} "
        f"--data {cfg['data']} --output {out_dir}"
    )

    # 2. Optional rendering
    traj_path = cfg.get("trajectory")
    if traj_path and Path(traj_path).exists():
        sh(
            f"nerfbaselines render --checkpoint {chk} --trajectory {traj_path}"
        )
    else:
        print("ℹ️  Render step skipped (no trajectory).")

    print("\n✔️  Done. Results saved to", out_dir)


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as e:
        sys.exit(e.returncode)
