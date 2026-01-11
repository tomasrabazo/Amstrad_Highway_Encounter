#!/usr/bin/env python3
"""
Basic Z80 Disassembler for HighwayEncounter.bin
"""

import struct
import sys

class Z80Disassembler:
    def __init__(self, data, start_addr=0x0000):
        self.data = data
        self.pos = 0
        self.start_addr = start_addr
        self.labels = {}  # Track labels for branches/jumps
        
    def read_byte(self):
        if self.pos >= len(self.data):
            return None
        byte = self.data[self.pos]
        self.pos += 1
        return byte
    
    def peek_byte(self, offset=0):
        if self.pos + offset >= len(self.data):
            return None
        return self.data[self.pos + offset]
    
    def read_word(self):
        if self.pos + 1 >= len(self.data):
            return None
        byte1 = self.data[self.pos]
        byte2 = self.data[self.pos + 1]
        self.pos += 2
        return byte1 | (byte2 << 8)
    
    def format_addr(self, addr):
        return f"L{addr:04X}"
    
    def get_label(self, addr):
        if addr not in self.labels:
            self.labels[addr] = self.format_addr(addr)
        return self.labels[addr]
    
    # Register names
    REG_8 = ['B', 'C', 'D', 'E', 'H', 'L', '(HL)', 'A']
    REG_16 = ['BC', 'DE', 'HL', 'SP']
    REG_16_ALT = ['BC', 'DE', 'HL', 'AF']
    COND = ['NZ', 'Z', 'NC', 'C', 'PO', 'PE', 'P', 'M']
    
    def disassemble_instruction(self):
        if self.pos >= len(self.data):
            return None, 0
        
        addr = self.start_addr + self.pos
        start_pos = self.pos
        
        opcode = self.read_byte()
        if opcode is None:
            return None, 0
        
        # Handle multi-byte opcodes
        if opcode == 0xCB:
            return self.disassemble_cb_prefix(addr)
        elif opcode == 0xED:
            return self.disassemble_ed_prefix(addr)
        elif opcode == 0xDD:
            return self.disassemble_dd_prefix(addr)  # IX prefix
        elif opcode == 0xFD:
            return self.disassemble_fd_prefix(addr)  # IY prefix
        
        # Main instruction set
        if opcode == 0x00:
            return "NOP", 1
        elif opcode == 0x01:
            word = self.read_word()
            return f"LD BC,&{word:04X}", 3
        elif opcode == 0x02:
            return "LD (BC),A", 1
        elif opcode == 0x03:
            return "INC BC", 1
        elif opcode == 0x04:
            return "INC B", 1
        elif opcode == 0x05:
            return "DEC B", 1
        elif opcode == 0x06:
            byte = self.read_byte()
            return f"LD B,&{byte:02X}", 2
        elif opcode == 0x07:
            return "RLCA", 1
        elif opcode == 0x08:
            return "EX AF,AF'", 1
        elif opcode == 0x09:
            return "ADD HL,BC", 1
        elif opcode == 0x0A:
            return "LD A,(BC)", 1
        elif opcode == 0x0B:
            return "DEC BC", 1
        elif opcode == 0x0C:
            return "INC C", 1
        elif opcode == 0x0D:
            return "DEC C", 1
        elif opcode == 0x0E:
            byte = self.read_byte()
            return f"LD C,&{byte:02X}", 2
        elif opcode == 0x0F:
            return "RRCA", 1
        
        # 0x10-0x1F
        elif opcode == 0x10:
            offset = self.read_byte()
            if offset > 127:
                offset -= 256
            target = addr + 2 + offset
            return f"DJNZ {self.get_label(target)}", 2
        elif opcode == 0x11:
            word = self.read_word()
            return f"LD DE,&{word:04X}", 3
        elif opcode == 0x12:
            return "LD (DE),A", 1
        elif opcode == 0x13:
            return "INC DE", 1
        elif opcode == 0x14:
            return "INC D", 1
        elif opcode == 0x15:
            return "DEC D", 1
        elif opcode == 0x16:
            byte = self.read_byte()
            return f"LD D,&{byte:02X}", 2
        elif opcode == 0x17:
            return "RLA", 1
        elif opcode == 0x18:
            offset = self.read_byte()
            if offset > 127:
                offset -= 256
            target = addr + 2 + offset
            return f"JR {self.get_label(target)}", 2
        elif opcode == 0x19:
            return "ADD HL,DE", 1
        elif opcode == 0x1A:
            return "LD A,(DE)", 1
        elif opcode == 0x1B:
            return "DEC DE", 1
        elif opcode == 0x1C:
            return "INC E", 1
        elif opcode == 0x1D:
            return "DEC E", 1
        elif opcode == 0x1E:
            byte = self.read_byte()
            return f"LD E,&{byte:02X}", 2
        elif opcode == 0x1F:
            return "RRA", 1
        
        # 0x20-0x2F
        elif 0x20 <= opcode <= 0x27:
            if opcode == 0x20:
                offset = self.read_byte()
                if offset > 127:
                    offset -= 256
                target = addr + 2 + offset
                return f"JR NZ,{self.get_label(target)}", 2
            elif opcode == 0x21:
                word = self.read_word()
                return f"LD HL,&{word:04X}", 3
            elif opcode == 0x22:
                word = self.read_word()
                return f"LD (&{word:04X}),HL", 3
            elif opcode == 0x23:
                return "INC HL", 1
            elif opcode == 0x24:
                return "INC H", 1
            elif opcode == 0x25:
                return "DEC H", 1
            elif opcode == 0x26:
                byte = self.read_byte()
                return f"LD H,&{byte:02X}", 2
            elif opcode == 0x27:
                return "DAA", 1
        
        # LD r,r (0x40-0x7F)
        elif 0x40 <= opcode <= 0x7F:
            src = (opcode >> 3) & 0x07
            dst = opcode & 0x07
            if opcode == 0x76:
                return "HALT", 1
            return f"LD {self.REG_8[dst]},{self.REG_8[src]}", 1
        
        # Arithmetic/logical operations (0x80-0xBF)
        elif 0x80 <= opcode <= 0xBF:
            op = opcode >> 3
            reg = opcode & 0x07
            ops = ['ADD', 'ADC', 'SUB', 'SBC', 'AND', 'XOR', 'OR', 'CP']
            return f"{ops[(op-0x10) & 0x07]} A,{self.REG_8[reg]}", 1
        
        # RET, POP, JP, CALL, PUSH (0xC0-0xFF)
        elif 0xC0 <= opcode <= 0xFF:
            if opcode == 0xC0:
                return "RET NZ", 1
            elif opcode == 0xC1:
                return "POP BC", 1
            elif opcode == 0xC2:
                word = self.read_word()
                return f"JP NZ,{self.get_label(word)}", 3
            elif opcode == 0xC3:
                word = self.read_word()
                return f"JP {self.get_label(word)}", 3
            elif opcode == 0xC4:
                word = self.read_word()
                return f"CALL NZ,{self.get_label(word)}", 3
            elif opcode == 0xC5:
                return "PUSH BC", 1
            elif opcode == 0xC6:
                byte = self.read_byte()
                return f"ADD A,&{byte:02X}", 2
            elif opcode == 0xC7:
                return "RST 0x00", 1
            elif opcode == 0xC8:
                return "RET Z", 1
            elif opcode == 0xC9:
                return "RET", 1
            elif opcode == 0xCA:
                word = self.read_word()
                return f"JP Z,{self.get_label(word)}", 3
            elif opcode == 0xCB:
                # Handled in prefix handler
                pass
            elif opcode == 0xCC:
                word = self.read_word()
                return f"CALL Z,{self.get_label(word)}", 3
            elif opcode == 0xCD:
                word = self.read_word()
                return f"CALL {self.get_label(word)}", 3
            elif opcode == 0xCE:
                byte = self.read_byte()
                return f"ADC A,&{byte:02X}", 2
            elif opcode == 0xCF:
                return "RST 0x08", 1
            elif opcode == 0xD0:
                return "RET NC", 1
            elif opcode == 0xD1:
                return "POP DE", 1
            elif opcode == 0xD2:
                word = self.read_word()
                return f"JP NC,{self.get_label(word)}", 3
            elif opcode == 0xD3:
                byte = self.read_byte()
                return f"OUT (&{byte:02X}),A", 2
            elif opcode == 0xD4:
                word = self.read_word()
                return f"CALL NC,{self.get_label(word)}", 3
            elif opcode == 0xD5:
                return "PUSH DE", 1
            elif opcode == 0xD6:
                byte = self.read_byte()
                return f"SUB &{byte:02X}", 2
            elif opcode == 0xD7:
                return "RST 0x10", 1
            elif opcode == 0xD8:
                return "RET C", 1
            elif opcode == 0xD9:
                return "EXX", 1
            elif opcode == 0xDA:
                word = self.read_word()
                return f"JP C,{self.get_label(word)}", 3
            elif opcode == 0xDB:
                byte = self.read_byte()
                return f"IN A,(&{byte:02X})", 2
            elif opcode == 0xDC:
                word = self.read_word()
                return f"CALL C,{self.get_label(word)}", 3
            elif opcode == 0xDD:
                # IX prefix - handled separately
                pass
            elif opcode == 0xDE:
                byte = self.read_byte()
                return f"SBC A,&{byte:02X}", 2
            elif opcode == 0xDF:
                return "RST 0x18", 1
            elif opcode == 0xE0:
                return "RET PO", 1
            elif opcode == 0xE1:
                return "POP HL", 1
            elif opcode == 0xE2:
                word = self.read_word()
                return f"JP PO,{self.get_label(word)}", 3
            elif opcode == 0xE3:
                return "EX (SP),HL", 1
            elif opcode == 0xE4:
                word = self.read_word()
                return f"CALL PO,{self.get_label(word)}", 3
            elif opcode == 0xE5:
                return "PUSH HL", 1
            elif opcode == 0xE6:
                byte = self.read_byte()
                return f"AND &{byte:02X}", 2
            elif opcode == 0xE7:
                return "RST 0x20", 1
            elif opcode == 0xE8:
                return "RET PE", 1
            elif opcode == 0xE9:
                return "JP (HL)", 1
            elif opcode == 0xEA:
                word = self.read_word()
                return f"JP PE,{self.get_label(word)}", 3
            elif opcode == 0xEB:
                return "EX DE,HL", 1
            elif opcode == 0xEC:
                word = self.read_word()
                return f"CALL PE,{self.get_label(word)}", 3
            elif opcode == 0xED:
                # Extended prefix - handled separately
                pass
            elif opcode == 0xEE:
                byte = self.read_byte()
                return f"XOR &{byte:02X}", 2
            elif opcode == 0xEF:
                return "RST 0x28", 1
            elif opcode == 0xF0:
                return "RET P", 1
            elif opcode == 0xF1:
                return "POP AF", 1
            elif opcode == 0xF2:
                word = self.read_word()
                return f"JP P,{self.get_label(word)}", 3
            elif opcode == 0xF3:
                return "DI", 1
            elif opcode == 0xF4:
                word = self.read_word()
                return f"CALL P,{self.get_label(word)}", 3
            elif opcode == 0xF5:
                return "PUSH AF", 1
            elif opcode == 0xF6:
                byte = self.read_byte()
                return f"OR &{byte:02X}", 2
            elif opcode == 0xF7:
                return "RST 0x30", 1
            elif opcode == 0xF8:
                return "RET M", 1
            elif opcode == 0xF9:
                return "LD SP,HL", 1
            elif opcode == 0xFA:
                word = self.read_word()
                return f"JP M,{self.get_label(word)}", 3
            elif opcode == 0xFB:
                return "EI", 1
            elif opcode == 0xFC:
                word = self.read_word()
                return f"CALL M,{self.get_label(word)}", 3
            elif opcode == 0xFD:
                # IY prefix - handled separately
                pass
            elif opcode == 0xFE:
                byte = self.read_byte()
                return f"CP &{byte:02X}", 2
            elif opcode == 0xFF:
                return "RST 0x38", 1
        
        # If we don't recognize it, output as data
        return f"DB &{opcode:02X}", 1
    
    def disassemble_cb_prefix(self, addr):
        """Handle CB prefix (bit operations, shifts, etc.)"""
        opcode = self.read_byte()
        if opcode is None:
            return "DB &CB", 1
        
        bit_op = (opcode >> 6) & 0x03
        reg = opcode & 0x07
        
        if bit_op == 0:
            ops = ['RLC', 'RRC', 'RL', 'RR', 'SLA', 'SRA', 'SLL', 'SRL']
            op = (opcode >> 3) & 0x07
            return f"{ops[op]} {self.REG_8[reg]}", 2
        elif bit_op == 1:
            bit = (opcode >> 3) & 0x07
            return f"BIT {bit},{self.REG_8[reg]}", 2
        elif bit_op == 2:
            bit = (opcode >> 3) & 0x07
            return f"RES {bit},{self.REG_8[reg]}", 2
        elif bit_op == 3:
            bit = (opcode >> 3) & 0x07
            return f"SET {bit},{self.REG_8[reg]}", 2
        
        return f"DB &CB,&{opcode:02X}", 2
    
    def disassemble_ed_prefix(self, addr):
        """Handle ED prefix (extended instructions)"""
        opcode = self.read_byte()
        if opcode is None:
            return "DB &ED", 1
        
        # Common ED instructions
        if opcode == 0x44 or opcode == 0x4C or opcode == 0x54 or opcode == 0x5C or opcode == 0x64 or opcode == 0x6C or opcode == 0x74 or opcode == 0x7C:
            return "NEG", 2
        elif opcode == 0x46 or opcode == 0x4E or opcode == 0x56 or opcode == 0x5E or opcode == 0x66 or opcode == 0x6E or opcode == 0x76 or opcode == 0x7E:
            return "IM 0", 2
        elif opcode == 0x57:
            return "LD A,I", 2
        elif opcode == 0x5F:
            return "LD A,R", 2
        elif opcode == 0x67:
            return "RRD", 2
        elif opcode == 0x6F:
            return "RLD", 2
        elif opcode == 0xA0:
            return "LDI", 2
        elif opcode == 0xA1:
            return "CPI", 2
        elif opcode == 0xA2:
            return "INI", 2
        elif opcode == 0xA3:
            return "OUTI", 2
        elif opcode == 0xA8:
            return "LDD", 2
        elif opcode == 0xA9:
            return "CPD", 2
        elif opcode == 0xAA:
            return "IND", 2
        elif opcode == 0xAB:
            return "OUTD", 2
        elif opcode == 0xB0:
            return "LDIR", 2
        elif opcode == 0xB1:
            return "CPIR", 2
        elif opcode == 0xB2:
            return "INIR", 2
        elif opcode == 0xB3:
            return "OTIR", 2
        elif opcode == 0xB8:
            return "LDDR", 2
        elif opcode == 0xB9:
            return "CPDR", 2
        elif opcode == 0xBA:
            return "INDR", 2
        elif opcode == 0xBB:
            return "OTDR", 2
        
        return f"DB &ED,&{opcode:02X}", 2
    
    def disassemble_dd_prefix(self, addr):
        """Handle DD prefix (IX register)"""
        opcode = self.read_byte()
        if opcode is None:
            return "DB &DD", 1
        
        # Simplified - just show it's an IX instruction
        if opcode == 0x21:
            word = self.read_word()
            return f"LD IX,&{word:04X}", 4
        elif opcode == 0xE1:
            return "POP IX", 2
        elif opcode == 0xE5:
            return "PUSH IX", 2
        elif opcode == 0xE9:
            return "JP (IX)", 2
        elif opcode == 0x36:
            byte = self.read_byte()
            offset = self.read_byte()
            if offset > 127:
                offset -= 256
            return f"LD (IX+&{offset:02X}),&{byte:02X}", 4
        
        return f"DB &DD,&{opcode:02X}", 2
    
    def disassemble_fd_prefix(self, addr):
        """Handle FD prefix (IY register)"""
        opcode = self.read_byte()
        if opcode is None:
            return "DB &FD", 1
        
        # Simplified - similar to IX
        if opcode == 0x21:
            word = self.read_word()
            return f"LD IY,&{word:04X}", 4
        elif opcode == 0xE1:
            return "POP IY", 2
        elif opcode == 0xE5:
            return "PUSH IY", 2
        elif opcode == 0xE9:
            return "JP (IY)", 2
        
        return f"DB &FD,&{opcode:02X}", 2
    
    def disassemble_all(self, max_lines=None):
        """Disassemble the entire binary"""
        output = []
        output.append(f"ORG &{self.start_addr:04X}\n")
        
        line_count = 0
        while self.pos < len(self.data):
            addr = self.start_addr + self.pos
            inst, size = self.disassemble_instruction()
            
            if inst is None:
                break
            
            # Create label if needed
            label_line = ""
            if addr in self.labels or self.peek_byte() == 0xCD:  # CALL instruction might create label
                label_line = f"{self.format_addr(addr)}:\n"
            
            output.append(f"{label_line}{inst}")
            
            line_count += 1
            if max_lines and line_count >= max_lines:
                break
        
        return "\n".join(output)


def main():
    if len(sys.argv) < 2:
        print("Usage: python disassemble_z80.py <binary_file> [output_file] [start_addr]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else input_file.replace('.bin', '_disasm.asm')
    start_addr = int(sys.argv[3], 16) if len(sys.argv) > 3 else 0x0000
    
    print(f"Reading {input_file}...")
    with open(input_file, 'rb') as f:
        data = f.read()
    
    print(f"File size: {len(data)} bytes")
    print(f"Starting disassembly from address &{start_addr:04X}...")
    
    disasm = Z80Disassembler(data, start_addr)
    
    # For large files, we might want to limit output
    # For now, let's do the whole file but note it might be slow
    print("Disassembling... (this may take a moment)")
    output = disasm.disassemble_all()
    
    print(f"Writing output to {output_file}...")
    with open(output_file, 'w') as f:
        f.write(output)
    
    print(f"Disassembly complete! Output written to {output_file}")
    print(f"Total bytes disassembled: {disasm.pos}")
    print(f"Labels created: {len(disasm.labels)}")


if __name__ == '__main__':
    main()
