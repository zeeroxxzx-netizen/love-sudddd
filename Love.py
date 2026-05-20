
import sys
import math
import random
import ctypes

# นำเข้าไลบรารีสำหรับทำ GUI และกราฟิก 3D
import tkinter as tk
from tkinter import ttk
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

# --- ตั้งค่าระดับความรักและข้อความภาษาไทย ---
LOVE_STATES = [
    {"text": "รักปกติ 🤍", "speed": 1.0, "color": (1.0, 0.42, 0.54)},     # สีชมพูอ่อน
    {"text": "รักมาก 💖", "speed": 2.2, "color": (1.0, 0.08, 0.57)},     # สีชมพูเข้ม (Neon)
    {"text": "รักที่สุด 💞", "speed": 3.8, "color": (1.0, 0.24, 0.24)},     # สีแดงเร่าร้อน
    {"text": "รักโคตรๆๆๆ 🔥🔥🔥", "speed": 5.5, "color": (1.0, 0.0, 0.33)} # สีแดงเข้มอมชมพู
]

class LoveHeartApp:
    def __init__(self):
        self.love_level = 0
        self.current_speed = 1.0
        self.target_speed = 1.0
        
        # มุมหมุนของหัวใจ
        self.angle_x = 0
        self.angle_y = 0
        
        # สร้างพิกัดอนุภาคทรงหัวใจ 3 มิติ
        self.particle_count = 1500
        self.particles = []
        self.generate_heart_particles()
        
        # สร้างหน้าต่างหลักด้วย Tkinter (ทำเป็นแดชบอร์ดควบคุม)
        self.root = tk.Tk()
        self.root.title("ระบบวัดชีพจรความรัก 3D")
        self.root.geometry("400x250")
        self.root.resizable(False, False)
        self.root.configure(bg="#0a0d14")
        
        # ปรับแต่งสไตล์ปุ่มและข้อความ
        self.setup_ui()
        
        # ฝังหน้าต่าง PyGame (OpenGL) ไว้ข้างๆ หรือเปิดแยก (ในที่นี้เปิดแยกเพื่อความเสถียรของเฟรมเรต)
        pygame.init()
        self.screen_width = 500
        self.screen_height = 500
        
        # สั่งให้หน้าต่าง Pygame ไปเปิดตรงตำแหน่งที่เหมาะสม
        import os
        os.environ['SDL_VIDEO_WINDOW_POS'] = "500,200"
        
        self.pygame_screen = pygame.display.set_mode(
            (self.screen_width, self.screen_height), 
            DOUBLEBUF | OPENGL
        )
        pygame.display.set_caption("3D Love Pulse")
        
        # ตั้งค่ามุมกล้อง OpenGL
        glViewport(0, 0, self.screen_width, self.screen_height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(60, (self.screen_width / self.screen_height), 0.1, 50.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        # เปิดระบบ Blend สีให้อนุภาคดูฟุ้งๆ นีออน
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE)
        glEnable(GL_PROGRAM_POINT_SIZE) # รองรับการปรับขนาดเม็ดพิกเซล
        
        # เริ่มจับเวลาสำหรับอนิเมชั่น
        self.clock = pygame.time.Clock()
        self.time_elapsed = 0.0
        
        # รันลูปอัปเดตกราฟิก
        self.update_all()

    def generate_heart_particles(self):
        """ คำนวณพิกัด 3D ทรงหัวใจด้วยสูตรคณิตศาสตร์ """
        self.particles = []
        for _ in range(self.particle_count):
            t = random.uniform(0, math.pi * 2)
            u = random.uniform(-math.pi/2, math.pi/2)
            
            # สูตรสมการหัวใจ 3 มิติ (สเกลให้พอดีหน้าจอ)
            scale = 0.35
            x = 16 * (math.sin(t) ** 3) * math.cos(u) * scale
            y = (13 * math.cos(t) - 5 * math.cos(2*t) - 2 * math.cos(3*t) - math.cos(4*t)) * math.cos(u) * scale
            z = 10 * math.sin(u) * math.sin(t) * scale
            
            # ใส่ Noise เล็กน้อยให้ดูพริ้วไหวธรรมชาติ
            noise = 0.05
            x += random.uniform(-noise, noise)
            y += random.uniform(-noise, noise)
            z += random.uniform(-noise, noise)
            
            self.particles.append([x, y, z])

    def setup_ui(self):
        """ วาดหน้าต่างควบคุมภาษาไทยให้แฟนกด """
        # ส่วนหัว
        title_label = tk.Label(
            self.root, text="ส่งรักให้เธอนะ 😊", 
            font=("Helvetica", 16, "bold"), fg="#ffffff", bg="#0a0d14"
        )
        title_label.pack(pady=15)
        
        # กรอบแสดงสถานะความรัก
        self.status_frame = tk.Frame(self.root, bg="#161b22", bd=1, relief="solid", padx=20, pady=10)
        self.status_frame.pack(pady=10, fill="x", padx=30)
        
        self.lbl_level = tk.Label(
            self.status_frame, text="ระดับความรู้สึก: 1 / 4", 
            font=("Helvetica", 10), fg="#8b949e", bg="#161b22"
        )
        self.lbl_level.pack()
        
        self.lbl_status = tk.Label(
            self.status_frame, text=LOVE_STATES[0]["text"], 
            font=("Helvetica", 18, "bold"), fg="#ff6b8b", bg="#161b22"
        )
        self.lbl_status.pack(pady=5)
        
        # กลุ่มปุ่มกด เพิ่ม-ลด ระดับ
        btn_frame = tk.Frame(self.root, bg="#0a0d14")
        btn_frame.pack(pady=15)
        
        btn_up = tk.Button(
            btn_frame, text="เพิ่มระดับความรัก 📈", font=("Helvetica", 11, "bold"),
            bg="#ff4b72", fg="white", width=16, command=self.increase_love
        )
        btn_up.pack(side="left", padx=10)
        
        btn_down = tk.Button(
            btn_frame, text="ลดระดับ 📉", font=("Helvetica", 11, "bold"),
            bg="#21262d", fg="#c9d1d9", width=10, command=self.decrease_love
        )
        btn_down.pack(side="left", padx=10)

    def increase_love(self):
        if self.love_level < 3:
            self.love_level += 1
            self.update_ui_text()
        else:
            self.lbl_status.config(text="รักเกินพิกัดแล้วเจ้าคนน่ารัก! 🥰")

    def decrease_love(self):
        if self.love_level > 0:
            self.love_level -= 1
            self.update_ui_text()
        else:
            self.lbl_status.config(text="ลดไม่ได้แล้ว รักน้อยกว่านี้ไม่ได้! 🥺")

    def update_ui_text(self):
        state = LOVE_STATES[self.love_level]
        self.lbl_level.config(text=f"ระดับความรู้สึก: {self.love_level + 1} / 4")
        self.lbl_status.config(text=state["text"])
        
        # เปลี่ยนสีตัวอักษรตามความแรงของความรัก
        hex_colors = ["#ff6b8b", "#ff1493", "#ff3e3e", "#ff0055"]
        self.lbl_status.config(fg=hex_colors[self.love_level])
        
        # ปรับเป้าหมายความเร็วชีพจร
        self.target_speed = state["speed"]

    def draw_heart_3d(self):
        """ ส่วนของการคำนวณและวาดกราฟิก 3D เม็ดทรายรูปหัวใจใน OpenGL """
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        
        # ถอยมุมกล้องออกมาระยะพอดีๆ
        glTranslatef(0.0, 0.0, -14.0)
        
        # หมุนแกนหัวใจตามเมาส์หรือหมุนอัตโนมัติช้าๆ
        glRotatef(self.angle_x, 1, 0, 0)
        glRotatef(self.angle_y, 0, 1, 0)
        
        # อัปเดตมุมหมุนเอื่อยๆ
        self.angle_y += 0.5
        
        # ค่อยๆ ปรับความเร็วชีพจรให้สมูท
        self.current_speed += (self.target_speed - self.current_speed) * 0.1
        
        # สูตรคลื่นหัวใจเต้นตึกตัก
        speed_factor = self.time_elapsed * 3.5 * self.current_speed
        pulse = 1.0 + 0.12 * (math.sin(speed_factor) ** 2) * math.cos(speed_factor * 0.5)
        
        # ดึงค่าสีประจำระดับปัจจุบัน
        color = LOVE_STATES[self.love_level]["color"]
        
        # วาดจุดอนุภาค
        glPointSize(3.0) # ขนาดเม็ดทราย 3D
        glBegin(GL_POINTS)
        
        for p in self.particles:
            # คำนวณระยะห่างเพื่อทำเอฟเฟกต์กระเพื่อมพริ้วๆ แตกต่างกันไปในแต่ละชั้น
            dist = math. some_dist = math.sqrt(p[0]**2 + p[1]**2 + p[2]**2)
            dynamic_pulse = pulse + math.sin(self.time_elapsed * 6.0 + dist * 0.5) * 0.02 * self.current_speed
            
            # ใส่สีแบบไล่เฉดสุ่มละอองแสง
            brightness = random.uniform(0.7, 1.0)
            glColor4f(color[0] * brightness, color[1] * brightness, color[2] * brightness, 0.8)
            
            # ขยายพิกัดตามจังหวะเต้น
            glVertex3f(p[0] * dynamic_pulse, p[1] * dynamic_pulse, p[2] * dynamic_pulse)
            
        glEnd()

    def update_all(self):
        """ ลูปหลักควบคุมการทำงานร่วมกันระหว่างหน้าต่างปุ่มกด และหน้าต่าง 3D """
        # 1. เช็คเหตุการณ์ของ Pygame (เช่นการปิดหน้าต่าง)
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                self.root.destroy()
                sys.exit()
                
        # 2. คำนวณเวลาที่ผ่านไปในเฟรมนี้
        dt = self.clock.tick(60) / 1000.0
        self.time_elapsed += dt
        
        # 3. วาดภาพ 3D ลงหน้าจอ OpenGL
        self.draw_heart_3d()
        pygame.display.flip()
        
        # 4. ให้โปรแกรมวนลูปอัปเดตตัวเองผ่าน Tkinter
        self.root.update_idletasks()
        self.root.update()
        
        # เรียกฟังก์ชันนี้ซ้ำในเฟรมถัดไป
        self.root.after(1, self.update_all)

if __name__ == "__main__":
    app = LoveHeartApp()


