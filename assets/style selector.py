import tkinter as tk
from tkinter import ttk, font as tkFont, colorchooser, filedialog
import json
import os

# --- Initial Style Values (Based on input_file_0.png) ---
INITIAL_STYLE = {
    "bg_color": "#5C1E84",  # Dark Purple base

    "title": {
        "text": "Trivia Royale",
        "fg": "#FDD835", # Gold
        "font_family": "Impact", # Approximated Bold font
        "font_size": 60,
        "font_bold": True,
        "font_italic": False,
        "pady": (40, 10) # Padding top, bottom
    },
    "divider": {
        "color": "#E1BEE7", # Lavender/off-white line
        "height": 1,
        "pady": (0, 5)
    },
    "scoreboard": {
        "text_left": "kelly; 0", # Note the semicolon from image
        "text_right": "kasha: 0",
        "fg": "#E1BEE7", # Lavender/off-white text
        "font_family": "Helvetica",
        "font_size": 18,
        "font_bold": False,
        "font_italic": False,
        "pady": (0, 20),
        "padx": 30, # Space from edges
        "separator_width": 15 # Space between score elements (adjust this)
    },
    "round_info": {
        "text_pattern": "Round {} / {} - Team: {}", # Template
        "fg": "#FDD835", # Gold
        "font_family": "Impact", # Approximated Bold font
        "font_size": 35,
        "font_bold": True,
        "font_italic": False,
        "pady": 30
    },
    "question": {
        "text": "In what year did the Berlin Wall fall?",
        "fg": "#FFFFFF", # White text
        "font_family": "Helvetica",
        "font_size": 26,
        "font_bold": False,
        "font_italic": False,
        "pady": 20,
        "wraplen_factor": 0.7 # % of window width
    },
    "prompt": {
        "text": "Press 'Enter' to reveal Answer",
        "fg": "#E0409A", # Magenta text
        "font_family": "Helvetica",
        "font_size": 24,
        "font_bold": False,
        "font_italic": True,
        "pady": 40
    }
}

# --- Main Application Class ---
class StyleAdjusterApp:
    def __init__(self, root):
        self.root = root # This is now the PREVIEW window
        self.root.title("Trivia Style Preview")
        # Make preview window larger initially
        win_width = 1000
        win_height = 700
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        center_x = int(screen_width/2 - win_width / 2) + 150 # Offset preview slightly right
        center_y = int(screen_height/2 - win_height / 2)
        root.geometry(f'{win_width}x{win_height}+{center_x}+{center_y}')
        root.minsize(600, 400) # Minimum preview size

        # Deep copy initial style
        self.current_style = json.loads(json.dumps(INITIAL_STYLE))

        # Get available fonts
        self.available_fonts = sorted([f for f in tkFont.families() if not f.startswith('@')])

        # --- Preview Frame (uses tk.Frame for easy BG) ---
        self.preview_frame = tk.Frame(self.root, relief=tk.SUNKEN, borderwidth=1) # Standard tk.Frame
        self.preview_frame.pack(fill=tk.BOTH, expand=True) # Fill the entire root window
        # Apply initial background color
        self.preview_frame.config(bg=self.current_style['bg_color'])


        # --- Control Window (Toplevel) ---
        self.control_window = tk.Toplevel(self.root)
        self.control_window.title("Style Controls")
        ctrl_width = 450
        ctrl_height = 700
        ctrl_center_x = center_x - ctrl_width - 10 # Position left of preview
        ctrl_center_y = center_y
        self.control_window.geometry(f'{ctrl_width}x{ctrl_height}+{ctrl_center_x}+{ctrl_center_y}')
        self.control_window.minsize(350, 500)

        # Make Control Window Content Scrollable
        self.control_canvas = tk.Canvas(self.control_window)
        self.control_scrollbar = ttk.Scrollbar(self.control_window, orient="vertical", command=self.control_canvas.yview)
        # Use ttk.Frame for consistent widget appearance in controls
        self.control_frame = ttk.Frame(self.control_canvas) # Frame inside canvas

        self.control_frame.bind(
            "<Configure>",
            lambda e: self.control_canvas.configure(
                scrollregion=self.control_canvas.bbox("all")
            )
        )

        self.control_canvas.create_window((0, 0), window=self.control_frame, anchor="nw")
        self.control_canvas.configure(yscrollcommand=self.control_scrollbar.set)

        # Pack scrollbar and canvas
        self.control_scrollbar.pack(side="right", fill="y")
        self.control_canvas.pack(side="left", fill="both", expand=True)


        # --- Status Bar (In Control Window) ---
        self.status_bar = ttk.Label(self.control_window, text="Ready.", anchor=tk.W, relief=tk.SUNKEN)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X, padx=2, pady=2)

        # Ensure controls close if main window closes
        self.root.protocol("WM_DELETE_WINDOW", self.quit_app)
        self.control_window.protocol("WM_DELETE_WINDOW", self.quit_app)


        # --- Populate Controls (into self.control_frame) ---
        self.populate_controls()

        # --- Initial Preview Render ---
        self.root.after(100, self.update_preview)


    def quit_app(self):
        """Close both windows."""
        try:
            if self.control_window and self.control_window.winfo_exists():
                self.control_window.destroy()
        except tk.TclError:
            pass
        try:
            if self.root and self.root.winfo_exists():
                self.root.destroy()
        except tk.TclError:
            pass

    # --- Control Population Methods (target self.control_frame) ---
    # (populate_controls, create_color_control, create_font_controls, etc.
    # are mostly unchanged, they just add widgets to self.control_frame now)

    def populate_controls(self):
        # This function now adds controls to self.control_frame
        row_num = 0

        # --- General Settings ---
        general_frame = ttk.LabelFrame(self.control_frame, text="General", padding=10)
        general_frame.grid(row=row_num, column=0, padx=10, pady=5, sticky="ew")
        row_num += 1
        # Use default pick_color for BG now, update_preview handles frame BG
        self.create_color_control(general_frame, "Background", "bg_color")

        # --- Element Controls ---
        for elem_key, elem_data in self.current_style.items():
            if isinstance(elem_data, dict) and "font_family" in elem_data:
                frame = ttk.LabelFrame(self.control_frame, text=elem_key.replace("_"," ").title(), padding=10)
                frame.grid(row=row_num, column=0, padx=10, pady=5, sticky="ew")
                self.control_frame.grid_columnconfigure(0, weight=1) # Ensure frame expands horizontally
                row_num += 1

                self.create_color_control(frame, "Text Color", f"{elem_key}.fg")
                self.create_font_controls(frame, elem_key)
                if "pady" in elem_data: self.create_padding_controls(frame, elem_key)
                if "padx" in elem_data: self.create_simple_scale_control(frame, "H. Padding (padx)", elem_key, "padx", 0, 100, 99)
                if "separator_width" in elem_data: self.create_simple_scale_control(frame, "Separator Width", elem_key, "separator_width", 0, 50, 100)

        # Divider controls
        divider_frame = ttk.LabelFrame(self.control_frame, text="Divider Line", padding=10)
        divider_frame.grid(row=row_num, column=0, padx=10, pady=5, sticky="ew")
        row_num += 1
        self.create_color_control(divider_frame, "Color", "divider.color")
        self.create_simple_scale_control(divider_frame, "Height", 'divider', 'height', 0, 5, 1)
        self.create_padding_controls(divider_frame, 'divider') # Reuse padding controls

        # --- Save Button ---
        save_button = ttk.Button(self.control_frame, text="Save Style to File...", command=self.save_style)
        save_button.grid(row=row_num, column=0, padx=10, pady=20, sticky="ew")

    def create_color_control(self, parent, label_text, style_key_path, command=None): # No change needed
        keys = style_key_path.split('.')
        try: initial_color = self.current_style[keys[0]] if len(keys) == 1 else self.current_style[keys[0]].get(keys[1], '#ffffff')
        except KeyError: initial_color = '#ffffff'
        frame = ttk.Frame(parent); frame.grid(sticky="ew", pady=2)
        ttk.Label(frame, text=f"{label_text}:").grid(row=0, column=0, padx=(0,5), sticky='w')
        color_swatch = tk.Label(frame, text="    ", bg=initial_color, relief=tk.SUNKEN, borderwidth=1); color_swatch.grid(row=0, column=1, padx=5)
        callback = command if command else lambda kp=style_key_path, swatch=color_swatch: self.pick_color(kp, swatch)
        button = ttk.Button(frame, text="Choose...", command=callback); button.grid(row=0, column=2)
        parent.grid_columnconfigure(2, weight=1)


    def pick_color(self, style_key_path, swatch_widget): # No change needed here, logic affects current_style
        keys = style_key_path.split('.')
        try: current_color = self.current_style[keys[0]] if len(keys) == 1 else self.current_style[keys[0]].get(keys[1], '#ffffff')
        except KeyError: current_color = '#ffffff'
        color_code = colorchooser.askcolor(title=f"Choose color for {style_key_path}", initialcolor=current_color)
        if color_code and color_code[1]:
            hex_color = color_code[1]
            swatch_widget.config(bg=hex_color)
            if len(keys) == 1: self.current_style[keys[0]] = hex_color
            else:
                if keys[0] not in self.current_style: self.current_style[keys[0]] = {}
                self.current_style[keys[0]][keys[1]] = hex_color
            self.update_preview() # Triggers redraw


    # Font and padding control creation methods unchanged (`create_font_controls`, `create_padding_controls`, `create_simple_scale_control`)
    # ... (Keep these methods as they were in the previous version) ...
    def create_font_controls(self, parent, elem_key):
        """Creates font family, size, bold, italic controls."""
        current_font_data = self.current_style.setdefault(elem_key, {})
        ttk.Label(parent, text="Font Family:").grid(row=1, column=0, sticky="w", pady=(5,0))
        font_combo = ttk.Combobox(parent, values=self.available_fonts, width=25)
        initial_font = current_font_data.get('font_family', 'Helvetica')
        if initial_font in self.available_fonts: font_combo.set(initial_font)
        elif self.available_fonts:
            font_combo.set(self.available_fonts[0]); current_font_data['font_family'] = self.available_fonts[0]; print(f"Warning: Font '{initial_font}' for {elem_key} not found. Defaulting to {self.available_fonts[0]}.")
        else: print("Warning: No fonts found!")
        font_combo.grid(row=1, column=1, sticky="ew")
        font_combo.bind("<<ComboboxSelected>>", lambda e, ek=elem_key: self.update_style(ek, 'font_family', e.widget.get()))
        initial_size = current_font_data.get('font_size', 12)
        self.create_simple_scale_control(parent, "Font Size", elem_key, "font_size", 8, 72, 2, default_value=initial_size)
        style_frame = ttk.Frame(parent); style_frame.grid(row=3, column=0, columnspan=2, sticky="w", pady=(5,0))
        bold_var = tk.BooleanVar(value=current_font_data.get('font_bold', False))
        bold_cb = ttk.Checkbutton(style_frame, text="Bold", variable=bold_var, command=lambda ek=elem_key, bv=bold_var: self.update_style(ek, 'font_bold', bv.get()))
        bold_cb.pack(side=tk.LEFT, padx=(0,10))
        italic_var = tk.BooleanVar(value=current_font_data.get('font_italic', False))
        italic_cb = ttk.Checkbutton(style_frame, text="Italic", variable=italic_var, command=lambda ek=elem_key, iv=italic_var: self.update_style(ek, 'font_italic', iv.get()))
        italic_cb.pack(side=tk.LEFT)

    def create_padding_controls(self, parent, elem_key):
        current_elem_style = self.current_style.setdefault(elem_key, {})
        pady_values = current_elem_style.get('pady', (5, 5))
        if not isinstance(pady_values, (list, tuple)) or len(pady_values) != 2:
            try: num_val = int(pady_values); pady_values = (num_val, num_val)
            except (TypeError, ValueError): pady_values = (5, 5)
        current_elem_style['pady'] = pady_values
        self.create_simple_scale_control(parent, "Padding Top", elem_key, None, 0, 100, 4, default_value=pady_values[0], command=lambda v, ek=elem_key: self.update_style_pady(ek, int(float(v)), 'top'))
        self.create_simple_scale_control(parent, "Padding Bottom", elem_key, None, 0, 100, 5, default_value=pady_values[1], command=lambda v, ek=elem_key: self.update_style_pady(ek, int(float(v)), 'bottom'))

    def create_simple_scale_control(self, parent, label_text, elem_key, prop_key, from_, to, grid_row, default_value=None, command=None):
        ttk.Label(parent, text=f"{label_text}:").grid(row=grid_row, column=0, sticky="w", pady=(5,0))
        if command is None: command = lambda v, ek=elem_key, pk=prop_key: self.update_style(ek, pk, int(float(v)))
        scale = ttk.Scale(parent, from_=from_, to=to, orient=tk.HORIZONTAL, length=150, command=command)
        if default_value is None and elem_key in self.current_style and prop_key is not None and prop_key in self.current_style[elem_key]: initial_value = self.current_style[elem_key].get(prop_key, from_)
        elif default_value is not None: initial_value = default_value
        else: initial_value = from_
        try: scale.set(initial_value)
        except (TypeError, tk.TclError): scale.set(from_); print(f"Warning: Invalid initial value '{initial_value}' for {elem_key}.{prop_key}. Resetting.") ;# Simplified error handling
        scale.grid(row=grid_row, column=1, sticky="ew")


    # --- Update and Helper Methods ---
    def update_style(self, elem_key, prop_key, value): # No change needed
        if elem_key not in self.current_style: self.current_style[elem_key] = {}
        self.current_style[elem_key][prop_key] = value
        self.update_preview()

    def update_style_pady(self, elem_key, value, side): # No change needed
        current_elem_style = self.current_style.setdefault(elem_key, {})
        pady_values = current_elem_style.get('pady', (5, 5))
        if not isinstance(pady_values, (list, tuple)) or len(pady_values) != 2:
            try: num_val = int(pady_values); pady_values = (num_val, num_val)
            except (TypeError, ValueError): pady_values = (5, 5)
        pady_list = list(pady_values)
        if side == 'top': pady_list[0] = value
        elif side == 'bottom': pady_list[1] = value
        elif side == 'both': pady_list = [value, value]
        self.current_style[elem_key]['pady'] = tuple(pady_list)
        self.update_preview()


    def get_font_tuple(self, elem_key): # Mostly unchanged, ensures validity
        style_data = self.current_style.setdefault(elem_key, {})
        family = style_data.get('font_family', 'Helvetica')
        size = style_data.get('font_size', 12)
        weight = 'bold' if style_data.get('font_bold', False) else 'normal'
        slant = 'italic' if style_data.get('font_italic', False) else 'roman'
        if family not in self.available_fonts:
            original_family = family
            family = 'Impact' if 'Impact' in self.available_fonts else ('Helvetica' if 'Helvetica' in self.available_fonts else (self.available_fonts[0] if self.available_fonts else "TkDefaultFont"))
            style_data['font_family'] = family # Update the dict
            print(f"Warning: Font '{original_family}' for {elem_key} not found. Using '{family}'.")

        style_str = f"{weight}"
        if slant == 'italic': style_str += f" {slant}"
        try:
             _ = tkFont.Font(family=family, size=size, weight=weight, slant=slant)
             return (family, size, style_str)
        except tk.TclError: print(f"Error creating font: {(family, size, style_str)}. Using default."); return ("Helvetica", 10, "normal")

    # --- Redraw Preview (targets self.preview_frame) ---
    def update_preview(self):
        """Clears and redraws the preview pane based on current_style."""
        for widget in self.preview_frame.winfo_children():
            widget.destroy()

        # --- Set background for tk.Frame directly ---
        bg_color = self.current_style.get("bg_color", "#FFFFFF")
        self.preview_frame.config(bg=bg_color) # Direct config for tk.Frame

        # Get dimensions for wrapping etc.
        self.preview_frame.update_idletasks()
        preview_w = self.preview_frame.winfo_width()
        preview_h = self.preview_frame.winfo_height()
        if preview_w < 50: preview_w = 800 # Estimate if too small

        # --- Recreate elements IN ORDER ---
        # Ensure 'bg' is set correctly for standard tk widgets inside
        try:
            # Title
            s = self.current_style.get('title', {})
            font_title = self.get_font_tuple('title')
            title_label = tk.Label(self.preview_frame, text=s.get('text',"Title"), font=font_title, fg=s.get('fg',"black"), bg=bg_color) # Use bg_color
            title_label.pack(side=tk.TOP, pady=s.get('pady', (5,5)))

            # Divider
            d = self.current_style.get('divider', {})
            div_pady = d.get('pady', (0,5))
            if not isinstance(div_pady, (list, tuple)): div_pady=(int(div_pady), int(div_pady))
            tk.Frame(self.preview_frame, height=d.get('height', 1), bg=d.get('color', 'grey')).pack(side=tk.TOP, fill=tk.X, pady=div_pady, padx=5)

            # Scoreboard Frame
            s = self.current_style.get('scoreboard',{})
            font_sb = self.get_font_tuple('scoreboard')
            sb_pady = s.get('pady',(0,5)); sb_padx = s.get('padx', 5); sb_sep = s.get('separator_width', 5); sb_fg = s.get('fg', 'black'); sb_text_l = s.get('text_left', 'L 0'); sb_text_r = s.get('text_right', 'R 0')
            if not isinstance(sb_pady, (list, tuple)): sb_pady=(int(sb_pady), int(sb_pady))

            sb_frame = tk.Frame(self.preview_frame, bg=bg_color) # Use bg_color
            sb_frame.pack(side=tk.TOP, fill=tk.X, pady=sb_pady)
            left_label = tk.Label(sb_frame, text=sb_text_l, font=font_sb, fg=sb_fg, bg=bg_color); left_label.pack(side=tk.LEFT, padx=(sb_padx, sb_sep))
            right_label = tk.Label(sb_frame, text=sb_text_r, font=font_sb, fg=sb_fg, bg=bg_color); right_label.pack(side=tk.RIGHT, padx=(sb_sep, sb_padx))

            # Round Info
            s = self.current_style.get('round_info',{})
            font_ri = self.get_font_tuple('round_info'); ri_pady = s.get('pady', 5)
            ri_text = s.get('text_pattern',"R {}/{}- T {}").format(1, 2, "kelly")
            round_label = tk.Label(self.preview_frame, text=ri_text, font=font_ri, fg=s.get('fg','black'), bg=bg_color); round_label.pack(side=tk.TOP, pady=ri_pady)

            # Question (packed before prompt)
            s_q = self.current_style.get('question',{})
            font_q = self.get_font_tuple('question'); q_pady = s_q.get('pady', 5);
            q_wraplen = int(preview_w * s_q.get('wraplen_factor', 0.7))
            question_label = tk.Label(self.preview_frame, text=s_q.get('text',"Question Text"), font=font_q, fg=s_q.get('fg','black'), bg=bg_color, wraplength=q_wraplen, justify=tk.CENTER);
            # Delay packing prompt slightly maybe? Pack question normally for now
            # We'll pack prompt with side=BOTTOM later

            # Prompt (Packed last relative to other top-level widgets using BOTTOM)
            s_p = self.current_style.get('prompt', {})
            font_p = self.get_font_tuple('prompt'); p_pady = s_p.get('pady', 5)
            prompt_label = tk.Label(self.preview_frame, text=s_p.get('text',"Prompt Text"), font=font_p, fg=s_p.get('fg','black'), bg=bg_color);
            prompt_label.pack(side=tk.BOTTOM, pady=p_pady, fill=tk.X) # Fill X for centering

            # Now pack the question, letting it fill the remaining space somewhat
            question_label.pack(side=tk.TOP, pady=q_pady, padx=10, fill=tk.BOTH, expand=True) # Let question expand

        except Exception as e:
             print(f"Error during preview update: {e}")
             try: # Try displaying error in preview window
                  tk.Label(self.preview_frame, text=f"Preview Error:\n{e}", fg="red", bg="white", wraplength=preview_w-20).pack(fill=tk.BOTH, expand=True)
             except: pass # Avoid error loop if preview fails

    # --- Save Method ---
    def save_style(self): # No change needed
        filename = filedialog.asksaveasfilename( title="Save Style As", defaultextension=".txt", filetypes=[("Text Files", "*.txt"), ("JSON Files", "*.json"), ("All Files", "*.*")] )
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f: json.dump(self.current_style, f, indent=4)
                self.status_bar.config(text=f"Style saved: {os.path.basename(filename)}") ; print(f"Style saved to {filename}")
            except Exception as e: self.status_bar.config(text=f"Error saving: {e}"); print(f"Error saving file: {e}")
        else: self.status_bar.config(text="Save cancelled.")

# --- Run the App ---
if __name__ == "__main__":
    root = tk.Tk()
    app = StyleAdjusterApp(root)
    root.mainloop()