import pyautogui as pag
import pyscreeze
import cv2
import numpy as np
import random
import time

def wait_for_image(img, timeout=10, interval=0.3, confidence=0.5, region=None):
    start = time.time()
    while time.time() - start < timeout:
        try:
            loc = pag.locateOnScreen(img, confidence=confidence, region=region)
            if loc:
                return loc
        except pag.ImageNotFoundException:
            pass
        time.sleep(interval)
    return None

# safe locate
def safe_locate(image, confidence=0.8):
    try:
        return pag.locateOnScreen(image, confidence=confidence)
    except (pyscreeze.ImageNotFoundException, pag.ImageNotFoundException):
        print(f"can't find the image: {image}")
        return None

# safe allocate
def safe_Alocate(image, confidence=0.8):
    try:
        return list(pag.locateAllOnScreen(image, confidence=confidence))  # chỉ lấy top 10
    except (pyscreeze.ImageNotFoundException, pag.ImageNotFoundException):
        print(f"can't find any locate in the image: {image}")
        return []



def is_gray_region(region):
    if not region:
        return False
    x, y, w, h = map(int, region)
    if w <= 0 or h <= 0:
        return False
    screenshot = pag.screenshot(region=(x, y, w, h))
    img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    mean_saturation = float(hsv[..., 1].mean())
    return mean_saturation < 40

# check_open_icon = False
while True:
    knight_loc = safe_locate("images/knight.png", confidence=0.5)
    if knight_loc: 
        pag.click(knight_loc)
        time.sleep(random.uniform(0.5, 1))
        continue

    cnt_rw = 0
    # find friend icon 
    friend_loc = safe_locate("images/friend.png", confidence=0.7)
    if friend_loc:
        # check_open_icon = True
        pag.click(friend_loc)

    
    community_loc = safe_locate("images/center.png", confidence=0.7)
    if community_loc:
        pag.moveTo(community_loc)
        center_loc = safe_locate("images/center.png", confidence=0.7)
        if center_loc:
            center = pag.center(center_loc)
            pag.moveTo(center)
            time_rand = random.uniform(0.3, 0.5)
            time.sleep(time_rand)
            pag.mouseDown()
            time_rand = random.uniform(0.2, 0.3)
            time.sleep(time_rand)
            pag.moveRel(-1500, 0, duration=0.5) 
            pag.mouseUp()
        else:
            print("Không thấy center.png, tiếp tục...")


        time.sleep(0.5)

        leaderboard_loc = safe_locate("images/leaderboard.png", confidence=0.7)
        if leaderboard_loc:
            pag.moveTo(leaderboard_loc)
            time_rand = random.uniform(0.3, 0.5) 
            time.sleep(time_rand)
            pag.mouseDown()
            time_rand = random.uniform(0.2, 0.3) 
            time.sleep(time_rand)
            pag.moveRel(-1500, 0, duration=0.5)  
            pag.mouseUp()
        else:
            print("Không thấy leaderboard")
        
        
        time.sleep(0.5)

        
        favorite_loc = safe_locate("images/favorite.png", confidence=0.7)
        if favorite_loc:
            x, y = favorite_loc.left, favorite_loc.top
            dx, dy = 250, 650
            click_x = int(x + dx)
            click_y = int(y + dy)
            time.sleep(0.5) 
            pag.click(click_x, click_y)
    
    # find attack and click
    attack_locs = safe_Alocate("images/attack.png", confidence=0.75)
    # loc_attack = None
    # if not attack_locs:
    #     continue
    if attack_locs is not None:
        for loc in attack_locs:
            region = (int(loc.left), int(loc.top), int(loc.width), int(loc.height))
            if not is_gray_region(region):
                loc_attack = loc
                pag.click(loc_attack)
        
    # ready to attack
    ready_loc = safe_locate("images/ready.png", confidence=0.7)
    if ready_loc :
        time.sleep(random.uniform(0.5,1))
        pag.click(ready_loc)
        exit_loc = safe_locate("images/exit.png", confidence=0.7)
        # sequence of action
        while exit_loc:
            # click to friend
            pag.click(exit_loc)    
            
            friend_loc = wait_for_image("images/friend.png", timeout=5, confidence=0.7, interval=0.2)
            if friend_loc:
                pag.click(friend_loc)
                time.sleep(1)
                
            gift_loc = wait_for_image("images/gift.png", timeout=5, confidence=0.7, interval=0.2)
            if gift_loc:
                pag.click(gift_loc)
                time.sleep(1)
                
            ticket_loc = wait_for_image("images/ticket.png", timeout=5, confidence=0.7, interval=0.2)
            if ticket_loc:
                pag.click(ticket_loc)
                time.sleep(1)
                
            exit_loc = wait_for_image("images/exit.png", timeout=5, confidence=0.7, interval=0.2)
            if exit_loc:
                pag.click(exit_loc)
                time.sleep(0.5)
            exit_loc = safe_locate("images/exit.png", confidence=0.7)
        
    
        # time.sleep(random.uniform(0.5,1))     

    # skip_loc = safe_locate("images/skip.png", confidence=0.7)
    # if skip_loc :
    #     pag.click(skip_loc)
    #     time.sleep(random.uniform(0.5,1)) 
    
    continue_loc = safe_locate("images/continue.png", confidence=0.8)
    if continue_loc :
        pag.click(continue_loc)
        time.sleep(random.uniform(0.5,1))
    
    sell_loc = safe_locate("images/sell.png", confidence=0.7)
    if sell_loc:
        sell_pos = sell_loc.left, sell_loc.top, 100, 50
        pag.click(sell_pos)

    clickcnt_loc = safe_locate("images/clicktocontinue.png", confidence=0.7)
    if clickcnt_loc :
        pag.click(clickcnt_loc)
        time.sleep(random.uniform(0.5,1))

    giveup_loc = safe_locate("images/giveup.png", confidence=0.7)
    if giveup_loc:
        x, y = giveup_loc.left, giveup_loc.top
        dx, dy = 200, 210
        click_x = x + dx
        click_y = y + dy
        time.sleep(0.5)  
        pag.click(click_x, click_y)
        time.sleep(1)  
        
        n_clicks = 10
        total_time = 2.5  
        delay = total_time / n_clicks
        for _ in range(n_clicks):
            pag.click(click_x, click_y)
            time.sleep(delay)
        continue

    reward_loc = safe_locate("images/reward.png", confidence=0.7)
    # list_rw = []
    if reward_loc :
        pag.click(reward_loc)
        time.sleep(random.uniform(0.5,1))
        reward_loc = safe_locate("images/reward.png", confidence=0.7)
    