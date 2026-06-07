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

        # To be implemented by the student.

        pass

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
