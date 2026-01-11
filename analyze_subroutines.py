#!/usr/bin/env python3
"""
Analyze Z80A assembly code to identify and extract subroutines
"""

import re
from collections import defaultdict

def analyze_subroutines(filename):
    """Analyze the assembly file and extract subroutine information"""
    
    with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
    
    # Pattern for labels
    label_pattern = re.compile(r'^L([0-9A-F]+):', re.IGNORECASE)
    
    # Pattern for CALL instructions
    call_pattern = re.compile(r'\bCALL\s+(?:NZ|Z|NC|C|PO|PE|P|M)?,?\s*L([0-9A-F]+)', re.IGNORECASE)
    
    # Pattern for RET instructions (excluding RETI)
    ret_pattern = re.compile(r'^\s+RET\s*(?:NZ|Z|NC|C|PO|PE|P|M)?\s*$', re.IGNORECASE)
    
    # Pattern for JP instructions to labels
    jp_pattern = re.compile(r'\bJP\s+(?:NZ|Z|NC|C|PO|PE|P|M)?,?\s*L([0-9A-F]+)', re.IGNORECASE)
    
    # Find all labels
    labels = {}
    for i, line in enumerate(lines, 1):
        match = label_pattern.search(line)
        if match:
            label = match.group(1).upper()
            if label not in labels:  # First occurrence
                labels[label] = i
    
    # Find all CALL instructions
    called_labels = set()
    call_sites = defaultdict(list)  # label -> list of lines that call it
    for i, line in enumerate(lines, 1):
        matches = call_pattern.findall(line)
        for label in matches:
            label = label.upper()
            called_labels.add(label)
            call_sites[label].append(i)
    
    # Find all JP instructions
    jp_labels = set()
    jp_sites = defaultdict(list)
    for i, line in enumerate(lines, 1):
        matches = jp_pattern.findall(line)
        for label in matches:
            label = label.upper()
            jp_labels.add(label)
            jp_sites[label].append(i)
    
    # Find RET instructions to identify subroutine boundaries
    ret_lines = []
    for i, line in enumerate(lines, 1):
        if ret_pattern.search(line):
            ret_lines.append(i)
    
    # Analyze subroutines that are called
    subroutines = []
    for label in sorted(called_labels):
        if label in labels:
            start_line = labels[label]
            # Find the next RET instruction after this label
            end_line = None
            for ret_line in ret_lines:
                if ret_line > start_line:
                    end_line = ret_line
                    break
            
            num_calls = len(call_sites[label])
            subroutines.append({
                'label': label,
                'start_line': start_line,
                'end_line': end_line,
                'num_calls': num_calls,
                'call_sites': call_sites[label][:5]  # First 5 call sites
            })
    
    return subroutines, labels, call_sites, len(lines)

def write_analysis_report(subroutines, total_lines, output_file):
    """Write analysis report to file"""
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("Z80A Assembly Code Subroutine Analysis\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Total lines in file: {total_lines:,}\n")
        f.write(f"Total subroutines called: {len(subroutines)}\n\n")
        f.write("=" * 60 + "\n\n")
        
        # Sort by start line
        subroutines.sort(key=lambda x: x['start_line'])
        
        # Group by approximate location (every 1000 lines)
        current_group = 0
        for sub in subroutines:
            group = sub['start_line'] // 1000
            if group != current_group:
                if current_group > 0:
                    f.write("\n")
                f.write(f"\n--- Subroutines in lines {group*1000:05d}-{(group+1)*1000:05d} ---\n\n")
                current_group = group
            
            f.write(f"Subroutine L{sub['label']}:\n")
            f.write(f"  Start line: {sub['start_line']}\n")
            if sub['end_line']:
                length = sub['end_line'] - sub['start_line']
                f.write(f"  End line: {sub['end_line']} (approx {length} lines)\n")
            else:
                f.write(f"  End line: Unknown\n")
            f.write(f"  Called from: {sub['num_calls']} location(s)\n")
            if sub['call_sites']:
                sites_str = ", ".join(str(s) for s in sub['call_sites'])
                if sub['num_calls'] > 5:
                    sites_str += f", ... ({sub['num_calls']-5} more)"
                f.write(f"  Call sites (sample): {sites_str}\n")
            f.write("\n")
        
        # Most frequently called subroutines
        f.write("\n" + "=" * 60 + "\n")
        f.write("Most Frequently Called Subroutines\n")
        f.write("=" * 60 + "\n\n")
        top_called = sorted(subroutines, key=lambda x: x['num_calls'], reverse=True)[:20]
        for sub in top_called:
            f.write(f"L{sub['label']}: {sub['num_calls']} calls (starts at line {sub['start_line']})\n")

if __name__ == '__main__':
    print("Analyzing HE.asm...")
    subroutines, labels, call_sites, total_lines = analyze_subroutines('HE.asm')
    
    print(f"Found {len(subroutines)} called subroutines")
    print(f"Total lines: {total_lines:,}")
    
    print("\nWriting analysis to subroutine_analysis.txt...")
    write_analysis_report(subroutines, total_lines, 'subroutine_analysis.txt')
    print("Analysis complete!")
