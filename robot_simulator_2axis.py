import tkinter as tk
from tkinter import ttk, messagebox
import math

class RobotSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("2-Axis Robot Arm Simulator - Visual Plus")
        self.root.geometry("1400x900")
        
        # --- State Variables ---
        self.l1 = 150.0
        self.l2 = 100.0
        self.theta1 = math.radians(45)
        self.theta2 = math.radians(45)
        self.target_x = 150.0
        self.target_y = 150.0
        
        # Scaling & Coordinate System (70% of current scale)
        self.scale = 1.75 
        self.offset_x = 450
        self.offset_y = 450 

        self.setup_ui()
        self.update_robot_drawing()

    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Left Side: Control Panel ---
        ctrl_panel = ttk.LabelFrame(main_frame, text="Control Panel", padding="15")
        ctrl_panel.pack(side=tk.LEFT, fill=tk.Y, padx=10)

        # 1. Link Configuration
        ttk.Label(ctrl_panel, text="1. Link Configuration", font=('Arial', 10, 'bold')).pack(anchor='w')
        self.l1_entry = self.create_input(ctrl_panel, "Link 1 Length:", 150)
        self.l2_entry = self.create_input(ctrl_panel, "Link 2 Length:", 100)
        ttk.Button(ctrl_panel, text="Apply Link Lengths", command=self.apply_links).pack(pady=5, fill='x')

        ttk.Separator(ctrl_panel, orient='horizontal').pack(fill='x', pady=15)

        # 2. Control Modes
        ttk.Label(ctrl_panel, text="2. Control Modes", font=('Arial', 10, 'bold')).pack(anchor='w')
        self.mode = tk.StringVar(value="FK")
        modes = [("FK Mode (Angles)", "FK"), ("IK Mode (Coord)", "IK"), 
                 ("Joystick Mode", "JOY"), ("Dual Slider Mode", "SLIDE")]
        for text, m in modes:
            ttk.Radiobutton(ctrl_panel, text=text, variable=self.mode, value=m, command=self.on_mode_change).pack(anchor='w', pady=2)

        ttk.Separator(ctrl_panel, orient='horizontal').pack(fill='x', pady=15)

        # 3. Parameter Inputs
        self.input_frame = ttk.Frame(ctrl_panel)
        self.input_frame.pack(fill='x')
        self.t1_entry = self.create_input(self.input_frame, "Theta 1 (deg):", 45)
        self.t2_entry = self.create_input(self.input_frame, "Theta 2 (deg):", 45)
        self.x_entry = self.create_input(self.input_frame, "Target X:", 150)
        self.y_entry = self.create_input(self.input_frame, "Target Y:", 150)
        
        ttk.Button(self.input_frame, text="Apply Position", command=self.handle_apply_pos).pack(pady=10, fill='x')

        # 4. Dual Sliders
        self.slider_frame = ttk.LabelFrame(ctrl_panel, text="X-Y Sliders")
        self.x_slide = ttk.Scale(self.slider_frame, from_=-400, to_=400, orient='horizontal', command=self.on_slider_move)
        self.y_slide = ttk.Scale(self.slider_frame, from_=400, to_=-400, orient='vertical', command=self.on_slider_move)
        
        # --- Right Side: Visualizer ---
        self.canvas = tk.Canvas(main_frame, bg="white", width=900, height=850, relief="ridge", bd=2)
        self.canvas.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.canvas.bind("<B1-Motion>", self.handle_joystick)
        self.canvas.bind("<Button-1>", self.handle_joystick)

    def create_input(self, parent, label, default):
        frame = ttk.Frame(parent)
        frame.pack(fill='x', pady=2)
        ttk.Label(frame, text=label, width=15).pack(side=tk.LEFT)
        ent = ttk.Entry(frame, width=10)
        ent.insert(0, str(default))
        ent.pack(side=tk.RIGHT)
        return ent

    def apply_links(self):
        try:
            new_l1 = float(self.l1_entry.get())
            new_l2 = float(self.l2_entry.get())
            if new_l1 <= 0 or new_l2 <= 0:
                messagebox.showerror("Workspace Error", "Lengths must be positive.")
                return
            self.l1, self.l2 = new_l1, new_l2
            self.update_robot_drawing()
        except ValueError:
            messagebox.showerror("Input Error", "Numerical values only.")

    def on_mode_change(self):
        m = self.mode.get()
        if m == "SLIDE":
            self.slider_frame.pack(fill='x', pady=10)
            self.x_slide.pack(fill='x', padx=5)
            self.y_slide.pack(pady=5)
        else:
            self.slider_frame.pack_forget()

    def handle_apply_pos(self):
        try:
            m = self.mode.get()
            if m == "FK":
                self.theta1 = math.radians(float(self.t1_entry.get()))
                self.theta2 = math.radians(float(self.t2_entry.get()))
                # Update target tracker to match result
                x1 = self.l1 * math.cos(self.theta1)
                y1 = self.l1 * math.sin(self.theta1)
                self.target_x = x1 + self.l2 * math.cos(self.theta1 + self.theta2)
                self.target_y = y1 + self.l2 * math.sin(self.theta1 + self.theta2)
            elif m == "IK":
                self.target_x = float(self.x_entry.get())
                self.target_y = float(self.y_entry.get())
                self.solve_ik(self.target_x, self.target_y, show_error=True)
            self.update_robot_drawing()
        except ValueError:
            messagebox.showerror("Input Error", "Invalid coordinates/angles.")

    def on_slider_move(self, _):
        if self.mode.get() == "SLIDE":
            self.target_x = self.x_slide.get()
            self.target_y = self.y_slide.get()
            self.solve_ik(self.target_x, self.target_y)
            self.update_robot_drawing()

    def handle_joystick(self, event):
        if self.mode.get() == "JOY":
            self.target_x = (event.x - self.offset_x) / self.scale
            self.target_y = (self.offset_y - event.y) / self.scale 
            self.solve_ik(self.target_x, self.target_y)
            self.update_robot_drawing()

    def solve_ik(self, x, y, show_error=False):
        d_sq = x**2 + y**2
        max_reach = (self.l1 + self.l2)**2
        min_reach = (self.l1 - self.l2)**2

        if min_reach <= d_sq <= max_reach:
            cos_t2 = (d_sq - self.l1**2 - self.l2**2) / (2 * self.l1 * self.l2)
            self.theta2 = math.acos(max(-1, min(1, cos_t2)))
            self.theta1 = math.atan2(y, x) - math.atan2(self.l2 * math.sin(self.theta2), self.l1 + self.l2 * math.cos(self.theta2))
            
            self.t1_entry.delete(0, tk.END)
            self.t1_entry.insert(0, f"{math.degrees(self.theta1):.2f}")
            self.t2_entry.delete(0, tk.END)
            self.t2_entry.insert(0, f"{math.degrees(self.theta2):.2f}")
        elif show_error:
            messagebox.showwarning("IK Exception", f"Point ({x}, {y}) unreachable.")
        
    def update_robot_drawing(self):
        self.canvas.delete("all")
        cx, cy = self.offset_x, self.offset_y
        
        # 1. Reachable Workspace Shading
        r_max = (self.l1 + self.l2) * self.scale
        r_min = abs(self.l1 - self.l2) * self.scale
        # Draw outer circle shaded
        self.canvas.create_oval(cx-r_max, cy-r_max, cx+r_max, cy+r_max, fill="#f0f7ff", outline="#d0e0f0", width=1)
        # Punch out inner circle (background color)
        if r_min > 5:
            self.canvas.create_oval(cx-r_min, cy-r_min, cx+r_min, cy+r_min, fill="white", outline="#f0f0f0", width=1)

        # 2. Target Crosshair (+)
        tx, ty = cx + self.target_x * self.scale, cy - self.target_y * self.scale
        self.canvas.create_line(tx-10, ty, tx+10, ty, fill="red", width=1) # Horizontal
        self.canvas.create_line(tx, ty-10, tx, ty+10, fill="red", width=1) # Vertical

        # 3. Robot Kinematics
        x1 = self.l1 * math.cos(self.theta1)
        y1 = self.l1 * math.sin(self.theta1)
        x2 = x1 + self.l2 * math.cos(self.theta1 + self.theta2)
        y2 = y1 + self.l2 * math.sin(self.theta1 + self.theta2)

        pts = [(cx, cy), (cx + x1*self.scale, cy - y1*self.scale), (cx + x2*self.scale, cy - y2*self.scale)]
        
        # 4. Links & Joints
        self.canvas.create_line(pts[0], pts[1], width=12, fill="#34495e", capstyle=tk.ROUND)
        self.canvas.create_line(pts[1], pts[2], width=8, fill="#2c3e50", capstyle=tk.ROUND)
        for px, py in pts:
            self.canvas.create_oval(px-6, py-6, px+6, py+6, fill="#e74c3c", outline="white")
        
        # 5. Overlays
        self.canvas.create_text(20, 20, anchor='nw', text=f"Target: ({self.target_x:.1f}, {self.target_y:.1f})", fill="red", font=('Consolas', 12, 'bold'))
        self.canvas.create_text(20, 45, anchor='nw', text=f"Actual TCP: ({x2:.1f}, {y2:.1f})", font=('Consolas', 11))

if __name__ == "__main__":
    root = tk.Tk()
    app = RobotSimulator(root)
    root.mainloop()