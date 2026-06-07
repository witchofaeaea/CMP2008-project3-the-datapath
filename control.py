class MainControl:
    def decode(self, opcode):
        signals = {
            'Reg2Loc': False, 'Branch': False, 'MemRead': False,
            'MemtoReg': False, 'ALUOp': 0, 'MemWrite': False,
            'ALUSrc': False, 'RegWrite': False
        }

        # To be implemented by the student.

        return signals


class ALUControl:
    def get_alu_control(self, alu_op, opcode):
        alu_control = 0

        # To be implemented by the student.

        return alu_control
