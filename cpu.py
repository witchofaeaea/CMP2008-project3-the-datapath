# Student information
# Name: Hatice
# Surname: Yaşasın
# ID: 2104423

from memory import InstructionMemory, DataMemory
from registers import RegisterFile
from control import MainControl, ALUControl
from alu import ALU


class LEGv8_CPU:
    def __init__(self, hex_file_path):
        self.pc = 0
        self.imem = InstructionMemory(hex_file_path)
        self.dmem = DataMemory()
        self.reg_file = RegisterFile()
        self.main_ctrl = MainControl()
        self.alu_ctrl = ALUControl()
        self.alu = ALU()
        self.halted = False

        self.current_instr = 0
        self.ctrl_signals = {}

    def run(self):
        cycle = 0
        print("--- Simulation Start ---")
        while not self.halted:
            self.step()
            if not self.halted:
                self.log_state(cycle)
            cycle += 1
        print("--- Simulation Halted ---")

    def step(self):
        self.current_instr = self.imem.read(self.pc)

        if self.current_instr == 0:
            self.halted = True
            return

        # Initialize/patch the register file if registers.py is still incomplete.
        if not hasattr(self.reg_file, "registers"):
            self.reg_file.registers = [0] * 32

            def read(reg1, reg2):
                val1 = 0 if reg1 == 31 else self.reg_file.registers[reg1]
                val2 = 0 if reg2 == 31 else self.reg_file.registers[reg2]
                return val1, val2

            def write(reg, value):
                if reg != 31:
                    self.reg_file.registers[reg] = value & 0xFFFFFFFFFFFFFFFF

            self.reg_file.read = read
            self.reg_file.write = write

        def sign_extend(value, bits):
            sign_bit = 1 << (bits - 1)
            return (value ^ sign_bit) - sign_bit

        def to_64bit(value):
            return value & 0xFFFFFFFFFFFFFFFF

        instr = self.current_instr
        old_pc = self.pc
        next_pc = old_pc + 4

        opcode_11 = (instr >> 21) & 0x7FF
        opcode_10 = (instr >> 22) & 0x3FF
        opcode_8 = (instr >> 24) & 0xFF
        opcode_6 = (instr >> 26) & 0x3F

        self.ctrl_signals = {
            'Reg2Loc': False,
            'Branch': False,
            'MemRead': False,
            'MemtoReg': False,
            'ALUOp': 0,
            'MemWrite': False,
            'ALUSrc': False,
            'RegWrite': False
        }

        # R-format: ADD, SUB
        if opcode_11 == 0b10001011000 or opcode_11 == 0b11001011000:
            rm = (instr >> 16) & 0x1F
            rn = (instr >> 5) & 0x1F
            rd = instr & 0x1F

            val_rn, val_rm = self.reg_file.read(rn, rm)

            if opcode_11 == 0b10001011000:
                result = val_rn + val_rm
            else:
                result = val_rn - val_rm

            self.reg_file.write(rd, to_64bit(result))

            self.ctrl_signals.update({
                'ALUOp': 2,
                'RegWrite': True
            })

        # I-format: ADDI, SUBI
        elif opcode_10 == 0b1001000100 or opcode_10 == 0b1101000100:
            imm12 = sign_extend((instr >> 10) & 0xFFF, 12)
            rn = (instr >> 5) & 0x1F
            rd = instr & 0x1F

            val_rn, _ = self.reg_file.read(rn, 31)

            if opcode_10 == 0b1001000100:
                result = val_rn + imm12
            else:
                result = val_rn - imm12

            self.reg_file.write(rd, to_64bit(result))

            self.ctrl_signals.update({
                'ALUOp': 2,
                'ALUSrc': True,
                'RegWrite': True
            })

        # D-format: LDUR, STUR
        elif opcode_11 == 0b11111000010 or opcode_11 == 0b11111000000:
            address = sign_extend((instr >> 12) & 0x1FF, 9)
            rn = (instr >> 5) & 0x1F
            rt = instr & 0x1F

            base_val, store_val = self.reg_file.read(rn, rt)
            mem_address = base_val + address

            if opcode_11 == 0b11111000010:
                data = self.dmem.read_word(mem_address)
                self.reg_file.write(rt, to_64bit(data))

                self.ctrl_signals.update({
                    'MemRead': True,
                    'MemtoReg': True,
                    'ALUSrc': True,
                    'RegWrite': True
                })

            else:
                self.dmem.write_word(mem_address, to_64bit(store_val))

                self.ctrl_signals.update({
                    'Reg2Loc': True,
                    'MemWrite': True,
                    'ALUSrc': True
                })

        # CB-format: CBZ
        elif opcode_8 == 0b10110100:
            imm19 = sign_extend((instr >> 5) & 0x7FFFF, 19)
            rt = instr & 0x1F

            val_rt, _ = self.reg_file.read(rt, 31)

            if val_rt == 0:
                next_pc = old_pc + (imm19 * 4)

            self.ctrl_signals.update({
                'Reg2Loc': False,
                'Branch': True,
                'ALUOp': 1
            })

        # B-format: B
        elif opcode_6 == 0b000101:
            imm26 = sign_extend(instr & 0x3FFFFFF, 26)
            next_pc = old_pc + (imm26 * 4)

            self.ctrl_signals.update({
                'Branch': True
            })

        else:
            print(f"Error: Unsupported instruction 0x{instr:08X}")
            self.halted = True
            return

        self.pc = next_pc

    def log_state(self, cycle):
        print(f"Cycle: {cycle}")
        print(f"PC: {self.pc}")
        print(f"Instruction: 0x{self.current_instr:08X}")

        if self.ctrl_signals:
            print("Control Signals:")
            for key, value in self.ctrl_signals.items():
                print(f"  {key}: {value}")
        else:
            print("Control Signals: [MISSING - Check step() implementation]")

        print("Registers (Non-Zero):")
        for i in range(32):
            val = self.reg_file.read(i, 31)[0]
            if val != 0:
                print(f"  X{i}: {val}")
        print("-" * 20)
        
