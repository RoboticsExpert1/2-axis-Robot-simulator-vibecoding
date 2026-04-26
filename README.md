# 🤖 Gemini x Python: 2-Axis Robot Arm Simulator (Visual Plus)

This project is an advanced 2-axis robot arm kinematics simulator developed through a collaboration between a mechanical engineer and **Google Gemini**. It expands upon the 1-axis model to demonstrate complex planar movements and inverse kinematics.

## 📺 Project Walkthrough
[![2-Axis Robot Simulator](https://i.ytimg.com/vi/https://youtu.be/HLWH0zgsJYQ?si=DFIe5YItsHDjb7jl/maxresdefault.jpg)](https://youtu.be/YOUR_VIDEO_ID)
> **Click the image above to watch the "Vibe Coding" process for this 2-axis system.**

## 🛠 Features
* **AI-Assisted UI & Logic:** GUI scaffolding and inverse kinematics solver drafted via **Gemini**.
* **Advanced Kinematics:** * **FK Mode:** Direct control of joint angles (Theta 1, Theta 2).
    * **IK Mode:** Automatic angle calculation based on target (X, Y) coordinates.
* **Interactive Control Suite:**
    * **Joystick Mode:** Real-time mouse tracking on the canvas.
    * **Dual Slider Mode:** Precise X-Y coordinate manipulation.
    * **Live Workspace Shading:** Visual representation of the robot's reachable area.
* **Expert Refinement:** 20 years of mechanical design expertise applied to ensure mathematical accuracy and "Kimchi-stew style" educational approach.

## 🧠 Engineering Note: Vibe Coding (Level 2)
This repository demonstrates the evolution of **"Vibe Coding"**. While the 1-axis model was a proof of concept, this 2-axis simulator handles non-linear equations for Inverse Kinematics. The engineer focuses on defining the **Workspace Constraints** and **Coordinate Offsets**, while Gemini rapidly iterates the `tkinter` event loops and `math` integration.

## 🚀 How to Run
1. Ensure you have Python installed.
2. No external libraries required (uses `tkinter` and `math` standard libraries).
3. Run the script:
   ```bash
   python robot_simulator_2axis.py
