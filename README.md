# CMP2008 Project 3 — LEGv8 Single-Cycle Datapath

## Overview

In this project you implement a **single-cycle LEGv8 CPU simulator** in Python. The simulator models how a processor fetches instructions, decodes them, asserts control signals, routes data through the datapath, accesses memory, and updates architectural state—all within one clock cycle per instruction.

This assignment connects ideas from computer organization: the datapath and control unit, register file behavior, ALU operation, and memory interfaces. Machine programs are provided as pre-encoded **`.hex` files**; you do not assemble source code for this project.

## Instruction set

The simulator supports a subset of LEGv8 instructions used in the course:

| Format | Instructions |
|--------|----------------|
| R-format | `ADD`, `SUB` |
| I-format | `ADDI`, `SUBI` |
| D-format | `LDUR`, `STUR` |
| CB-format | `CBZ` |
| B-format | `B` |

Programs terminate when the simulator fetches an instruction word of `0x00000000` (HALT).

## Repository layout

| Component | Role |
|-----------|------|
| `cpu.py` | Top-level CPU: simulation loop, fetch, and datapath wiring in `step()` |
| `control.py` | Main control unit and ALU control unit |
| `alu.py` | Arithmetic/logic unit |
| `registers.py` | Register file |
| `memory.py` | Instruction memory and data memory (provided) |
| `run_cpu.py` | Run the simulator on a given `.hex` program |
| `auto_grade.py` | Run all test programs and report a score |
| `test_cases/` | Machine-code test programs (`.hex`) |

Some modules are fully specified; others contain marked sections for your implementation.

## Simulation model

The design follows a **single-cycle** organization: each call to `step()` completes fetch, decode, execute, memory access, write-back, and PC update for one instruction. The provided `run()` method drives the simulation and prints per-cycle state (PC, instruction, control signals, non-zero registers) until HALT.

Control signals follow the LEGv8-style naming used in the course (for example `RegWrite`, `MemRead`, `ALUSrc`, `Branch`, `MemtoReg`, `Reg2Loc`, and `ALUOp`). The ALU is driven by a separate ALU control field derived from the main control unit and instruction opcode.

## Testing

Test programs under `test_cases/` exercise individual instruction formats, combined behavior, and selected edge cases (zero register, branches, signed immediates, memory offsets, and similar). You can run the simulator on any test file with `run_cpu.py`.

Correctness is evaluated against reference simulation output for these programs. Your implementation should produce matching cycle-by-cycle logs, including control signal values and final register state.

You can check your grade by running `auto_grade.py`.


