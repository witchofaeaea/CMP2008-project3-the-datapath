#!/usr/bin/env python3
"""Run a LEGv8 CPU simulation against one machine-code test file."""

from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path


def _clear_project_modules() -> None:
    for name in ("cpu", "control", "alu", "registers", "memory"):
        sys.modules.pop(name, None)


def load_cpu_class(use_reference: bool, solution_dir: Path | None = None):
    project_root = Path(__file__).resolve().parent

    if solution_dir is not None:
        solution_dir = solution_dir.resolve()
        _clear_project_modules()
        sys.path.insert(0, str(solution_dir))
        from cpu import LEGv8_CPU

        return LEGv8_CPU

    if use_reference:
        ref_path = project_root / "instructor_only" / "cpu_reference.py"
        spec = importlib.util.spec_from_file_location("legv8_cpu_reference", ref_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.LEGv8_CPU

    from cpu import LEGv8_CPU

    return LEGv8_CPU


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the LEGv8 CPU simulator.")
    parser.add_argument(
        "hex_file",
        nargs="?",
        help="Path to a machine-code .hex file",
    )
    parser.add_argument(
        "--reference",
        action="store_true",
        help="Run instructor_only/cpu_reference.py instead of student cpu.py",
    )
    parser.add_argument(
        "--solution-dir",
        default=None,
        help="Run modules from this directory (e.g. solution/)",
    )
    args = parser.parse_args()

    if args.reference and args.solution_dir:
        print("Error: use only one of --reference or --solution-dir", file=sys.stderr)
        return 1

    if not args.hex_file:
        parser.print_help()
        return 1

    hex_path = Path(args.hex_file)
    if not hex_path.exists():
        print(f"Error: file not found: {hex_path}", file=sys.stderr)
        return 1

    project_root = Path(__file__).resolve().parent
    solution_dir = None
    if args.solution_dir:
        solution_dir = (project_root / args.solution_dir).resolve()

    cpu_class = load_cpu_class(args.reference, solution_dir)
    cpu = cpu_class(str(hex_path))
    cpu.run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
