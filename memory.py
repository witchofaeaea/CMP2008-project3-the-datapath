class InstructionMemory:
    def __init__(self, hex_file_path):
        self.memory = {} # Word-addressable for simplicity in instructions
        self._load_memory(hex_file_path)

    def _load_memory(self, file_path):
        address = 0
        try:
            with open(file_path, 'r') as f:
                for line in f:
                    hex_str = line.strip()
                    if hex_str:
                        # Store as 32-bit integers
                        self.memory[address] = int(hex_str, 16)
                        address += 4 # LEGv8 instructions are 4 bytes
        except FileNotFoundError:
            print(f"Error: Instruction file '{file_path}' not found.")

    def read(self, address):
        # Return 0 (halt) if out of bounds
        return self.memory.get(address, 0)

class DataMemory:
    def __init__(self):
        self.memory = {} # Byte-addressable

    def read_word(self, address):
        # LEGv8 LDUR reads 64 bits (8 bytes)
        value = 0
        for i in range(8):
            byte_val = self.memory.get(address + i, 0)
            # Little Endian: LSB at lowest address
            value |= (byte_val << (8 * i))
        return value

    def write_word(self, address, write_data):
        # LEGv8 STUR writes 64 bits (8 bytes)
        for i in range(8):
             # Extract byte
             byte_val = (write_data >> (8 * i)) & 0xFF
             self.memory[address + i] = byte_val