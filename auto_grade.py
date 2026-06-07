#!/usr/bin/env python3
"""Auto-grader for the LEGv8 CPU simulator (Project 3)."""

from __future__ import annotations

import argparse
import difflib
import importlib.util
import io
import sys
from contextlib import redirect_stdout
from pathlib import Path
from typing import Type


def _clear_project_modules() -> None:
    for name in ("cpu", "control", "alu", "registers", "memory"):
        sys.modules.pop(name, None)


def load_cpu_class(use_reference: bool, solution_dir: Path | None = None) -> Type:
    """Load CPU from student files, solution/, or instructor_only/."""
    project_root = Path(__file__).resolve().parent

    if solution_dir is not None:
        solution_dir = solution_dir.resolve()
        if not solution_dir.is_dir():
            raise FileNotFoundError(f"solution directory not found: {solution_dir}")
        _clear_project_modules()
        sys.path.insert(0, str(solution_dir))
        from cpu import LEGv8_CPU

        return LEGv8_CPU

    if use_reference:
        ref_path = project_root / "instructor_only" / "cpu_reference.py"
        if not ref_path.exists():
            raise FileNotFoundError(f"reference CPU not found: {ref_path}")
        spec = importlib.util.spec_from_file_location("legv8_cpu_reference", ref_path)
        if spec is None or spec.loader is None:
            raise ImportError(f"failed to load {ref_path}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.LEGv8_CPU

    from cpu import LEGv8_CPU

    return LEGv8_CPU


WEIGHTS = {
    "test_r_format.hex": 8,
    "test_i_format.hex": 8,
    "test_d_format.hex": 16,
    "test_cb_format.hex": 16,
    "test_b_format.hex": 8,
    "test_all.hex": 9,
    "test_edge_x31.hex": 5,
    "test_edge_cbz_not_taken.hex": 5,
    "test_edge_cbz_taken.hex": 5,
    "test_edge_negative_imm.hex": 5,
    "test_edge_d_negative.hex": 5,
    "test_edge_mem_uninit.hex": 5,
    "test_edge_sub_wrap.hex": 5,
}

assert sum(WEIGHTS.values()) == 100, "WEIGHTS must total 100 points"


def read_student_info(path: Path) -> dict[str, str]:
    info = {"Name": "", "Surname": "", "ID": ""}
    if not path.exists():
        return info

    with path.open("r", encoding="utf-8") as fh:
        for _ in range(20):
            line = fh.readline()
            if not line:
                break
            stripped = line.strip()
            if not stripped.startswith("#"):
                continue
            content = stripped.lstrip("#").strip()
            if ":" not in content:
                continue
            key, value = content.split(":", 1)
            key = key.strip()
            if key in info:
                info[key] = value.strip()
    return info


def run_simulation(
    hex_path: Path,
    cpu_class: Type,
    max_cycles: int = 1000,
) -> tuple[bool, str, str]:
    buffer = io.StringIO()
    try:
        with redirect_stdout(buffer):
            cpu = cpu_class(str(hex_path))
            print("--- Simulation Start ---")
            cycle = 0
            while not cpu.halted and cycle < max_cycles:
                cpu.step()
                if not cpu.halted:
                    cpu.log_state(cycle)
                cycle += 1

            if cpu.halted:
                print("--- Simulation Halted ---")
            else:
                return (
                    False,
                    buffer.getvalue(),
                    f"simulation did not halt within {max_cycles} cycles",
                )
    except Exception as exc:
        return False, "", f"{type(exc).__name__}: {exc}"
    return True, buffer.getvalue(), ""


def compare_output(actual: str, expected_path: Path) -> tuple[bool, str]:
    expected = expected_path.read_text(encoding="utf-8")
    if actual == expected:
        return True, ""

    diff = difflib.unified_diff(
        expected.splitlines(),
        actual.splitlines(),
        fromfile=f"expected/{expected_path.name}",
        tofile="student/output",
        lineterm="",
    )
    return False, "\n".join(diff)


def main() -> int:
    parser = argparse.ArgumentParser(description="Grade LEGv8 CPU simulator output.")
    parser.add_argument(
        "--student-file",
        default="cpu.py",
        help="Student file checked only for header info (default: cpu.py)",
    )
    parser.add_argument(
        "--reference",
        action="store_true",
        help="Grade using instructor_only/cpu_reference.py (does not use student cpu.py)",
    )
    parser.add_argument(
        "--solution-dir",
        default=None,
        help="Grade modules from this directory (e.g. solution/)",
    )
    args = parser.parse_args()

    if args.reference and args.solution_dir:
        print("ERROR: use only one of --reference or --solution-dir", file=sys.stderr)
        return 1

    project_root = Path(__file__).resolve().parent
    solution_dir = None
    if args.solution_dir:
        solution_dir = (project_root / args.solution_dir).resolve()

    try:
        cpu_class = load_cpu_class(args.reference, solution_dir)
    except (FileNotFoundError, ImportError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    test_dir = project_root / "test_cases"
    expected_dir = project_root / "expected_outputs"
    student_file = project_root / args.student_file

    if args.reference:
        cpu_label = "instructor_only/cpu_reference.py"
    elif args.solution_dir:
        cpu_label = f"{args.solution_dir}/"
    else:
        cpu_label = "cpu.py (student)"
    print(f"CPU implementation: {cpu_label}")
    print(f"Student info file: {student_file.name}")
    student_info = read_student_info(student_file)
    print("Student info:")
    print(f"  Name:    {student_info['Name'] or 'N/A'}")
    print(f"  Surname: {student_info['Surname'] or 'N/A'}")
    print(f"  ID:      {student_info['ID'] or 'N/A'}")
    print()

    if not test_dir.exists():
        print(f"ERROR: missing test directory: {test_dir}", file=sys.stderr)
        return 1
    if not expected_dir.exists():
        print(f"ERROR: missing expected output directory: {expected_dir}", file=sys.stderr)
        return 1

    test_files = sorted(test_dir.glob("*.hex"))
    if not test_files:
        print(f"ERROR: no .hex files found in {test_dir}", file=sys.stderr)
        return 1

    print("Grading rubric:")
    max_score = 0
    for test_file in test_files:
        points = WEIGHTS.get(test_file.name, 0)
        if points:
            print(f"  {test_file.name}: {points} points")
            max_score += points
    print(f"Total available: {max_score} points")
    print()

    total_score = 0
    failed_tests: list[str] = []

    for test_file in test_files:
        points = WEIGHTS.get(test_file.name, 0)
        expected_path = expected_dir / f"{test_file.stem}.out"
        if not expected_path.exists():
            print(f"ERROR: missing expected output: {expected_path}", file=sys.stderr)
            return 1

        ok, actual, error = run_simulation(test_file, cpu_class)
        if not ok:
            failed_tests.append(test_file.name)
            print(f"FAIL  {test_file.name}: +0 points")
            print(f"  Runtime error: {error}")
            print()
            continue

        passed, diff = compare_output(actual, expected_path)
        if passed:
            total_score += points
            print(f"PASS  {test_file.name}: +{points} points")
        else:
            failed_tests.append(test_file.name)
            print(f"FAIL  {test_file.name}: +0 points")
            print(diff)
            print()

    print("---")
    print(f"Total score: {total_score}/{max_score}")
    if failed_tests:
        print("Failed tests:")
        for name in failed_tests:
            print(f"  - {name}")
    elif total_score == max_score:
        print("All tests passed!")

    return 0 if total_score == max_score else 2


if __name__ == "__main__":
    raise SystemExit(main())
