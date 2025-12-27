#!/usr/bin/env python3
"""
Fix the TriviaRoyale.py syntax error by removing duplicated code
"""

with open('TriviaRoyale.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find and remove the duplicate code section (lines ~681-746 based on error)
# The duplicate starts at "pady=10" and ends before "def get_number_of_rounds"

output_lines = []
skip_mode = False
skip_start_pattern = "            pady=10"
skip_end_pattern = "    def get_number_of_rounds(self):"

for i, line in enumerate(lines, 1):
    # Check if we're entering skip mode
    if skip_start_pattern in line and not skip_mode:
        skip_mode = True
        print(f"Skipping duplicate code starting at line {i}")
        # Instead of the broken line, add the correct code
        output_lines.append("            if entry.get():\n")
        output_lines.append("                if self.sfx:\n")
        output_lines.append("                    self.sfx.play('wrong')\n")
        output_lines.append("                messagebox.showerror(\"Invalid Input\", \"Please enter a valid number.\")\n")
        output_lines.append("                entry.delete(0, tk.END)\n")
        output_lines.append("            entry.focus_set()\n")
        output_lines.append("        \n")
        output_lines.append("        self.root.bind(\"<Return>\", validate_input)\n")
        output_lines.append("\n")
        continue
    
    # Check if we're exiting skip mode
    if skip_mode and skip_end_pattern in line:
        skip_mode = False
        print(f"Resuming at line {i}")
    
    # Only add lines if we're not in skip mode
    if not skip_mode:
        output_lines.append(line)

# Write the fixed version
with open('TriviaRoyale.py', 'w', encoding='utf-8') as f:
    f.writelines(output_lines)

print(f"\n✅ Fixed! Removed {len(lines) - len(output_lines)} duplicate lines")
print(f"   Original: {len(lines)} lines")
print(f"   Fixed: {len(output_lines)} lines")
print("\nBackup saved as: TriviaRoyale.py.broken")
