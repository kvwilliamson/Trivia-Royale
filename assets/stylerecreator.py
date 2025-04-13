import tkinter as tk
from tkinter import Canvas

def create_gradient(canvas, width, height, color1="#ff7bcd", color2="#2b19b0"):
    """
    Creates a vertical gradient on the canvas from color1 (top) to color2 (bottom).
    This approach draws individual horizontal lines with interpolated colors.
    """
    def hex_to_rgb(hex_color):
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    r1, g1, b1 = hex_to_rgb(color1[1:])
    r2, g2, b2 = hex_to_rgb(color2[1:])
    
    for i in range(height):
        ratio = i / height
        r = int(r1 + (r2 - r1) * ratio)
        g = int(g1 + (g2 - g1) * ratio)
        b = int(b1 + (b2 - b1) * ratio)
        color = f"#{r:02x}{g:02x}{b:02x}"
        canvas.create_line(0, i, width, i, fill=color)

def create_ui():
    root = tk.Tk()
    root.title("Trivia Royale")
    root.geometry("600x400")
    root.resizable(False, False)

    # Main canvas for gradient
    canvas = Canvas(root, width=600, height=400, highlightthickness=0)
    canvas.pack(fill="both", expand=True)
    
    # Draw the gradient background
    create_gradient(canvas, 600, 400)
    
    # ------------------
    # Title
    # ------------------
    canvas.create_text(
        300, 40, 
        text="Trivia Royale", 
        font=("Helvetica", 24, "bold"), 
        fill="yellow"
    )
    
    # ------------------
    # Scoreboard
    # ------------------
    canvas.create_text(
        100, 70, 
        text="Kelly: 30", 
        font=("Helvetica", 16, "bold"), 
        fill="yellow"
    )
    canvas.create_text(
        500, 70, 
        text="Kasha: 20", 
        font=("Helvetica", 16, "bold"), 
        fill="yellow"
    )
    
    # ------------------
    # Round Number
    # ------------------
    canvas.create_text(
        300, 100,
        text="Round 5",
        font=("Helvetica", 16, "bold"),
        fill="yellow"
    )
    
    # ------------------
    # Question Box
    # ------------------
    box_top = 140
    box_bottom = 220
    canvas.create_rectangle(
        50, box_top, 550, box_bottom,
        #fill="black",
        outline="yellow",
        width=2
    )
    canvas.create_text(
        300, (box_top + box_bottom) / 2,
        text="What is the capital of France?",
        font=("Helvetica", 20, "bold"),
        fill="yellow",
        width=480
    )
    
    # ------------------
    # Instructions
    # ------------------
    canvas.create_text(
        300, 270,
        text="Press Enter to Reveal Answer",
        font=("Helvetica", 14),
        fill="yellow"
    )
    canvas.create_text(
        300, 300,
        text="Press Space for Next Turn",
        font=("Helvetica", 14),
        fill="yellow"
    )

    root.mainloop()

if __name__ == "__main__":
    create_ui()
