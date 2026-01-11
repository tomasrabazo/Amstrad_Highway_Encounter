# Z80A Assembly Code Structure Analysis
## Highway Encounter (Amstrad CPC)

### Overview
- **Total lines:** 54,635
- **Total subroutines identified:** 220 called subroutines
- **Code format:** Disassembled Z80A assembly code for Amstrad CPC

### Analysis Method
The code has been analyzed to identify all subroutines that are called via `CALL` instructions. Each subroutine entry point has been cataloged with:
- Starting line number
- Number of call sites
- Sample call locations

---

## Most Frequently Called Subroutines

These are the core routines that appear throughout the code:

1. **L3F00** - 64 calls (line 11702) - Most frequently called
2. **L1338** - 57 calls (line 3490) - Very frequently used
3. **L1B4F** - 38 calls (line 4802) - Frequently used
4. **L1F00** - 29 calls (line 5404)
5. **L7F00** - 18 calls (line 25749)
6. **L1C62** - 15 calls (line 4958)
7. **L0F00** - 14 calls (line 2733)
8. **L2EE3** - 14 calls (line 8156)
9. **L0000** - 11 calls (line 4) - Very early in code
10. **L03F3** - 11 calls (line 815) - I/O operations

---

## Key Subroutines by Function Area

### I/O and Hardware Control (Early Addresses)
- **L03F3** (line 815) - I/O port operations (port &7F - likely PPI/CRTC control)
- **L03FF** (line 824) - I/O wait loop (reads port &F5, waits for condition)
- **L0411** (line 842) - Called 8 times, appears to be I/O related
- **L0426** (line 857) - I/O operations

### Memory Operations
- **L0078** (line 157) - Iterates through data structure at L5600, processes entries
- **L0923** (line 1744) - Memory copy operations, works with screen memory areas
- **L0C6E** (line 2306) - Graphics/screen operations (addresses like L9905, L9A1B suggest screen memory)

### Game Logic Routines
- **L1338** (line 3490) - 57 calls - Likely a core game loop or update function
- **L1B4F** (line 4802) - 38 calls - Frequently called game logic
- **L2EE3** (line 8156) - 14 calls - Game logic subroutine

### Initialization
- **L0000** (line 4) - Very early code, called 11 times - Possibly initialization or reset code

---

## Code Structure Observations

1. **Early Memory Range (L0000-L0FFF)**: Contains initialization code, I/O routines, and basic utilities
2. **Mid Range (L1000-L2FFF)**: Appears to contain game logic, update routines, and core functions
3. **Higher Addresses (L3000+)**: Likely contains data tables, graphics data, and specialized routines

### Subroutine Naming Pattern
All subroutines follow the pattern `Lxxxx:` where `xxxx` is a 4-digit hexadecimal number representing the memory address.

---

## Next Steps for Understanding the Code

1. **Focus on High-Usage Routines**: Start with L3F00, L1338, and L1B4F as they're called most frequently
2. **Trace Initialization**: Follow L0000 and early code to understand program startup
3. **Identify Data Structures**: Look for memory areas referenced (L5600, L6500, L9905, etc.)
4. **Map I/O Operations**: Understand hardware interactions via L03F3, L03FF routines

---

## Full Subroutine List

See `subroutine_analysis.txt` for the complete list of all 220 subroutines with their locations and call sites.

---

## Notes

- This appears to be disassembled machine code (note the many EQU statements and NOP instructions)
- Some code areas may contain data tables rather than executable code
- The code uses index registers (IX, IY) extensively for structured data access
- I/O port addresses suggest this is Amstrad CPC specific code:
  - Port &7F: PPI control
  - Port &F5: FDC (Floppy Disk Controller) or similar
