import tkinter as tk
from tkinter import ttk, messagebox
import threading
import pyautogui as pag
import pyscreeze
import cv2
import numpy as np
import random
import time

class GameAutomationGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Game Automation Control Panel")
        self.root.geometry("600x800")
        self.root.configure(bg='#2b2b2b')
        
        # Variables
        self.running = False
        self.automation_thread = None
        
        # Image confidence settings
        self.confidence_vars = {
            'gagoy.png': tk.DoubleVar(value=0.5),
            'friend.png': tk.DoubleVar(value=0.7),
            'center.png': tk.DoubleVar(value=0.7),
            'history.png': tk.DoubleVar(value=0.7),
            'favorite.png': tk.DoubleVar(value=0.7),
            'full_attack.png': tk.DoubleVar(value=0.9),
            'attack.png': tk.DoubleVar(value=0.45),
            'comeback.png': tk.DoubleVar(value=0.7),
            'exit.png': tk.DoubleVar(value=0.7),
            'ready.png': tk.DoubleVar(value=0.7),
            'gift.png': tk.DoubleVar(value=0.7),
            'ticket.png': tk.DoubleVar(value=0.7),
            'continue.png': tk.DoubleVar(value=0.8),
            'sell.png': tk.DoubleVar(value=0.7),
            'clicktocontinue.png': tk.DoubleVar(value=0.7),
            'giveup.png': tk.DoubleVar(value=0.7),
            'reward.png': tk.DoubleVar(value=0.7),
        }
        
        # Automation state
        self.mark = {}
        self.reg_clicked = None
        self.cnt_mark = 0
        
        self.setup_gui()
        
    def setup_gui(self):
        # Title
        title_label = tk.Label(
            self.root, 
            text="🎮 Game Automation Controller", 
            font=("Arial", 16, "bold"),
            bg='#2b2b2b',
            fg='#ffffff'
        )
        title_label.pack(pady=10)
        
        # Main frame
        main_frame = tk.Frame(self.root, bg='#2b2b2b')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20)
        
        # Control buttons frame
        control_frame = tk.Frame(main_frame, bg='#2b2b2b')
        control_frame.pack(fill=tk.X, pady=10)
        
        # Start/Stop buttons
        self.start_btn = tk.Button(
            control_frame,
            text="▶️ Start Automation",
            command=self.start_automation,
            bg='#4CAF50',
            fg='white',
            font=("Arial", 12, "bold"),
            relief=tk.RAISED,
            bd=3
        )
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = tk.Button(
            control_frame,
            text="⏹️ Stop Automation",
            command=self.stop_automation,
            bg='#f44336',
            fg='white',
            font=("Arial", 12, "bold"),
            relief=tk.RAISED,
            bd=3,
            state=tk.DISABLED
        )
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        # Status label
        self.status_label = tk.Label(
            control_frame,
            text="Status: Stopped",
            font=("Arial", 10),
            bg='#2b2b2b',
            fg='#ffffff'
        )
        self.status_label.pack(side=tk.RIGHT)
        
        # Separator
        separator = ttk.Separator(main_frame, orient='horizontal')
        separator.pack(fill=tk.X, pady=10)
        
        # Confidence settings frame
        settings_label = tk.Label(
            main_frame,
            text="🎯 Image Recognition Confidence Settings",
            font=("Arial", 14, "bold"),
            bg='#2b2b2b',
            fg='#ffffff'
        )
        settings_label.pack(pady=(0, 10))
        
        # Scrollable frame for sliders
        canvas = tk.Canvas(main_frame, bg='#2b2b2b', highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#2b2b2b')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Create sliders for each image
        for i, (image_name, var) in enumerate(self.confidence_vars.items()):
            self.create_slider(scrollable_frame, image_name, var, i)
        
        # Log frame
        log_frame = tk.Frame(self.root, bg='#2b2b2b')
        log_frame.pack(fill=tk.X, padx=20, pady=10)
        
        log_label = tk.Label(
            log_frame,
            text="📋 Activity Log",
            font=("Arial", 12, "bold"),
            bg='#2b2b2b',
            fg='#ffffff'
        )
        log_label.pack(anchor=tk.W)
        
        # Log text widget
        self.log_text = tk.Text(
            log_frame,
            height=8,
            bg='#1e1e1e',
            fg='#ffffff',
            font=("Courier", 9),
            wrap=tk.WORD
        )
        log_scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        
        self.log_text.pack(side="left", fill="both", expand=True)
        log_scrollbar.pack(side="right", fill="y")
        
    def create_slider(self, parent, image_name, var, row):
        frame = tk.Frame(parent, bg='#2b2b2b')
        frame.pack(fill=tk.X, pady=2, padx=10)
        
        # Image name label
        name_label = tk.Label(
            frame,
            text=image_name,
            font=("Arial", 10),
            bg='#2b2b2b',
            fg='#ffffff',
            width=20,
            anchor='w'
        )
        name_label.pack(side=tk.LEFT, padx=5)
        
        # Slider
        slider = tk.Scale(
            frame,
            from_=0.1,
            to=1.0,
            resolution=0.05,
            orient=tk.HORIZONTAL,
            variable=var,
            bg='#3b3b3b',
            fg='#ffffff',
            highlightbackground='#2b2b2b',
            troughcolor='#1e1e1e',
            length=200
        )
        slider.pack(side=tk.LEFT, padx=10)
        
        # Value label
        value_label = tk.Label(
            frame,
            textvariable=var,
            font=("Arial", 10),
            bg='#2b2b2b',
            fg='#ffffff',
            width=8
        )
        value_label.pack(side=tk.LEFT, padx=5)
        
    def log_message(self, message):
        """Add message to log with timestamp"""
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
    def start_automation(self):
        if not self.running:
            self.running = True
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
            self.status_label.config(text="Status: Running", fg='#4CAF50')
            
            # Start automation in separate thread
            self.automation_thread = threading.Thread(target=self.run_automation, daemon=True)
            self.automation_thread.start()
            
            self.log_message("🚀 Automation started")
            
    def stop_automation(self):
        self.running = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.status_label.config(text="Status: Stopped", fg='#f44336')
        self.log_message("⏹️ Automation stopped")
        
    def get_confidence(self, image_name):
        """Get current confidence value for an image"""
        return self.confidence_vars[image_name].get()
        
    # Original automation functions with logging
    def wait_for_image(self, img, timeout=10, interval=0.3, confidence=0.5, region=None):
        start = time.time()
        while time.time() - start < timeout and self.running:
            try:
                loc = pag.locateOnScreen(img, confidence=confidence, region=region)
                if loc:
                    return loc
            except pag.ImageNotFoundException:
                pass
            time.sleep(interval)
        return None

    def safe_locate(self, image, confidence=0.8):
        try:
            return pag.locateOnScreen(image, confidence=confidence)
        except (pyscreeze.ImageNotFoundException, pag.ImageNotFoundException):
            return None

    def safe_Alocate(self, image, confidence=0.8):
        try:
            return list(pag.locateAllOnScreen(image, confidence=confidence))
        except (pyscreeze.ImageNotFoundException, pag.ImageNotFoundException):
            return []

    def iou(self, boxA, boxB):
        xA, yA, wA, hA = boxA
        xB, yB, wB, hB = boxB
        x1A, y1A, x2A, y2A = xA, yA, xA + wA, yA + hA
        x1B, y1B, x2B, y2B = xB, yB, xB + wB, yB + hB

        inter_x1 = max(x1A, x1B)
        inter_y1 = max(y1A, y1B)
        inter_x2 = min(x2A, x2B)
        inter_y2 = min(y2A, y2B)

        inter_w = max(0, inter_x2 - inter_x1)
        inter_h = max(0, inter_y2 - inter_y1)
        inter_area = inter_w * inter_h

        areaA = (x2A - x1A) * (y2A - y1A)
        areaB = (x2B - x1B) * (y2B - y1B)
        union = areaA + areaB - inter_area
        if union == 0:
            return 0.0
        return inter_area / union

    def deduplicate_boxes(self, box_tuples, iou_thresh=0.5):
        sorted_boxes = sorted(box_tuples, key=lambda t: (t[1], t[0]))
        kept = []
        kept_boxes = []
        for (x, y, w, h, loc) in sorted_boxes:
            cur = (x, y, w, h)
            duplicate = False
            for kb in kept_boxes:
                if self.iou(cur, kb) > iou_thresh:
                    duplicate = True
                    break
            if not duplicate:
                kept.append((x, y, w, h, loc))
                kept_boxes.append(cur)
        return kept

    def is_gray_region(self, region):
        if not region:
            return False
        x, y, w, h = map(int, region)
        if w <= 0 or h <= 0:
            return False
        try:
            screenshot = pag.screenshot(region=(x, y, w, h))
            img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            mean_saturation = float(hsv[..., 1].mean())
            return mean_saturation < 40
        except Exception:
            return False

    def has_iou_with_true(self, region, mark, iou_thresh=0.45):
        for r, val in mark.items():
            if r is None:
                continue
            if self.iou(region, r) >= iou_thresh:
                return val
        return False
        
    def run_automation(self):
        """Main automation loop"""
        self.log_message("🔄 Starting automation loop...")
        
        while self.running:
            try:
                # Check for gagoy
                gagoy_loc = self.safe_locate("images/gagoy.png", confidence=self.get_confidence('gagoy.png'))
                if gagoy_loc and self.running:
                    pag.click(gagoy_loc)
                    self.log_message("🎯 Clicked gagoy")
                    time.sleep(random.uniform(0.5, 1))
                    continue

                # Find friend icon
                friend_loc = self.safe_locate("images/friend.png", confidence=self.get_confidence('friend.png'))
                if friend_loc and self.running:
                    pag.click(friend_loc)
                    self.log_message("👥 Clicked friend icon")

                # Community actions
                community_loc = self.safe_locate("images/center.png", confidence=self.get_confidence('center.png'))
                if community_loc and self.running:
                    self.log_message("🏛️ Found community center")
                    pag.moveTo(community_loc)
                    center_loc = self.safe_locate("images/center.png", confidence=self.get_confidence('center.png'))
                    if center_loc:
                        center = pag.center(center_loc)
                        pag.moveTo(center)
                        time.sleep(random.uniform(0.3, 0.5))
                        pag.mouseDown()
                        time.sleep(random.uniform(0.2, 0.3))
                        pag.moveRel(-1500, 0, duration=0.5)
                        pag.mouseUp()
                        self.log_message("↔️ Performed center swipe")

                    time.sleep(random.uniform(0.5, 1))

                    # History actions
                    his_loc = self.safe_locate("images/history.png", confidence=self.get_confidence('history.png'))
                    if his_loc and self.running:
                        pag.moveTo(his_loc)
                        time.sleep(random.uniform(0.3, 0.5))
                        pag.mouseDown()
                        time.sleep(random.uniform(0.2, 0.3))
                        pag.moveRel(-1500, 0, duration=0.5)
                        pag.mouseUp()
                        self.log_message("📜 Performed history swipe")

                    time.sleep(random.uniform(0.3, 0.6))

                    # Favorite actions
                    favorite_loc = self.safe_locate("images/favorite.png", confidence=self.get_confidence('favorite.png'))
                    if favorite_loc and self.running:
                        x, y = favorite_loc.left, favorite_loc.top
                        dx, dy = 250, 650
                        click_x = int(x + dx)
                        click_y = int(y + dy)
                        time.sleep(0.6)
                        pag.click(click_x, click_y)
                        self.log_message("⭐ Clicked favorite")

                # Scroll for full attack
                full_attack_loc = self.safe_locate("images/full_attack.png", confidence=self.get_confidence('full_attack.png'))
                if full_attack_loc and self.running:
                    screen_width, screen_height = pag.size()
                    center_x, center_y = screen_width // 2, screen_height // 2
                    pag.moveTo(center_x, center_y, duration=0.3)
                    pag.dragRel(0, -500, duration=0.5, button='left')
                    self.log_message("📜 Scrolled for full attack")

                # Find and click attack
                if self.running:
                    attack_locs = self.safe_Alocate("images/attack.png", confidence=self.get_confidence('attack.png'))
                    if attack_locs:
                        raw_boxes = [(int(l.left), int(l.top), int(l.width), int(l.height), l) for l in attack_locs]
                        unique = self.deduplicate_boxes(raw_boxes, iou_thresh=0.45)
                        unique = unique[:10]

                        for (x, y, w, h, loc) in unique:
                            if not self.running:
                                break
                            region = (x, y, w, h)
                            if region not in self.mark:
                                self.mark[region] = False
                            if not self.is_gray_region(region) and self.mark[region] == False:
                                pag.click(region)
                                self.reg_clicked = region
                                self.log_message(f"⚔️ Attacked region {region}")
                                time.sleep(random.uniform(0.7, 1))
                                self.cnt_mark += 1
                                break
                            if self.mark[region] == True and self.cnt_mark >= 5:
                                self.mark[region] = False
                                self.cnt_mark = 0

                # Handle comeback
                comeback_loc = self.safe_locate("images/comeback.png", confidence=self.get_confidence('comeback.png'))
                while comeback_loc and self.running:
                    self.mark[self.reg_clicked] = True
                    comeback_pos = comeback_loc.left, comeback_loc.top, 450, 450
                    pag.click(comeback_pos)
                    self.log_message("🔄 Handled comeback")
                    exit_loc = self.wait_for_image("images/exit.png", timeout=5, 
                                                 confidence=self.get_confidence('exit.png'), interval=0.2)
                    time.sleep(random.uniform(0.7, 1))
                    if exit_loc:
                        pag.click(exit_loc)
                    comeback_loc = self.safe_locate("images/comeback.png", confidence=self.get_confidence('comeback.png'))

                # Handle ready to attack
                ready_loc = self.safe_locate("images/ready.png", confidence=self.get_confidence('ready.png'))
                if ready_loc and self.running:
                    self.log_message("✅ Ready to attack")
                    time.sleep(random.uniform(1.3, 1.6))
                    pag.click(ready_loc)
                    exit_loc = self.safe_locate("images/exit.png", confidence=self.get_confidence('exit.png'))
                    
                    # Sequence of actions
                    while exit_loc and self.running:
                        time.sleep(1.5)
                        pag.click(exit_loc)
                        
                        friend_loc = self.wait_for_image("images/friend.png", timeout=5, 
                                                       confidence=self.get_confidence('friend.png'), interval=0.2)
                        if friend_loc:
                            pag.click(friend_loc)
                            time.sleep(random.uniform(1, 1.3))
                            
                        gift_loc = self.wait_for_image("images/gift.png", timeout=5, 
                                                     confidence=self.get_confidence('gift.png'), interval=0.2)
                        if gift_loc:
                            pag.click(gift_loc)
                            self.log_message("🎁 Collected gift")
                            time.sleep(random.uniform(1, 1.3))
                            
                        ticket_loc = self.wait_for_image("images/ticket.png", timeout=5, 
                                                       confidence=self.get_confidence('ticket.png'), interval=0.2)
                        if ticket_loc:
                            pag.click(ticket_loc)
                            self.log_message("🎫 Used ticket")
                            time.sleep(random.uniform(1, 1.3))
                            
                        exit_loc = self.wait_for_image("images/exit.png", timeout=5, 
                                                     confidence=self.get_confidence('exit.png'), interval=0.2)
                        if exit_loc:
                            pag.click(exit_loc)
                            time.sleep(1.6)
                        exit_loc = self.safe_locate("images/exit.png", confidence=self.get_confidence('exit.png'))

                # Handle other UI elements
                continue_loc = self.safe_locate("images/continue.png", confidence=self.get_confidence('continue.png'))
                if continue_loc and self.running:
                    pag.click(continue_loc)
                    self.log_message("➡️ Clicked continue")
                    time.sleep(random.uniform(0.5, 1))

                sell_loc = self.safe_locate("images/sell.png", confidence=self.get_confidence('sell.png'))
                if sell_loc and self.running:
                    sell_pos = sell_loc.left, sell_loc.top, 100, 50
                    pag.click(sell_pos)
                    self.log_message("💰 Clicked sell")

                clickcnt_loc = self.safe_locate("images/clicktocontinue.png", confidence=self.get_confidence('clicktocontinue.png'))
                if clickcnt_loc and self.running:
                    pag.click(clickcnt_loc)
                    self.log_message("👆 Clicked to continue")
                    time.sleep(random.uniform(0.5, 1))

                giveup_loc = self.safe_locate("images/giveup.png", confidence=self.get_confidence('giveup.png'))
                if giveup_loc and self.running:
                    x, y = giveup_loc.left, giveup_loc.top
                    dx, dy = 200, 210
                    click_x = x + dx
                    click_y = y + dy
                    time.sleep(0.6)
                    pag.click(click_x, click_y)
                    self.log_message("🏳️ Gave up - rapid clicking")
                    time.sleep(random.uniform(1, 1.3))
                    
                    # Rapid clicking
                    n_clicks = 10
                    total_time = 2.5
                    delay = total_time / n_clicks
                    for _ in range(n_clicks):
                        if not self.running:
                            break
                        pag.click(click_x, click_y)
                        time.sleep(delay)
                    continue

                reward_loc = self.safe_locate("images/reward.png", confidence=self.get_confidence('reward.png'))
                if reward_loc and self.running:
                    pag.click(reward_loc)
                    self.log_message("🏆 Collected reward")
                    time.sleep(random.uniform(0.5, 1))
                    
                time.sleep(0.1)  # Small delay to prevent excessive CPU usage
                
            except Exception as e:
                self.log_message(f"❌ Error: {str(e)}")
                time.sleep(1)
                
        self.log_message("🛑 Automation loop ended")

def main():
    # Create root window
    root = tk.Tk()
    
    # Create and run the GUI
    app = GameAutomationGUI(root)
    
    # Handle window close
    def on_closing():
        if app.running:
            app.stop_automation()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Center window on screen
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f"{width}x{height}+{x}+{y}")
    
    # Start the GUI
    root.mainloop()

if __name__ == "__main__":
    main()