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

def iou(boxA, boxB):
    # box = (x, y, w, h)
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

def deduplicate_boxes(box_tuples, iou_thresh=0.5):
    # sắp xếp theo y rồi x để có thứ tự lặp ổn định (trên xuống, trái phải)
    sorted_boxes = sorted(box_tuples, key=lambda t: (t[1], t[0]))
    kept = []
    kept_boxes = []  # (x,y,w,h) để so IOU nhanh
    for (x, y, w, h, loc) in sorted_boxes:
        cur = (x, y, w, h)
        duplicate = False
        for kb in kept_boxes:
            if iou(cur, kb) > iou_thresh:
                duplicate = True
                break
        if not duplicate:
            kept.append((x, y, w, h, loc))
            kept_boxes.append(cur)
    return kept

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

def has_iou_with_true(region, mark, iou_thresh=0.45):
    """Kiểm tra xem region có IoU >= iou_thresh với region nào đang True trong mark không."""
    for r, val in mark.items():
        if r is None:
            continue
        if iou(region, r) >= iou_thresh:
            return val
    return False

import cv2
import numpy as np
import pyautogui as pag

# def is_gray_region(region, downscale=1, sat_thresh=30, diff_thresh=15, frac_thresh=0.90, debug=False):
#     if not region:
#         return False
#     try:
#         x, y, w, h = map(int, region)
#     except Exception:
#         return False
#     if w <= 0 or h <= 0:
#         return False

#     try:
#         screenshot = pag.screenshot(region=(x, y, w, h))  # PIL Image, RGB
#     except Exception as e:
#         if debug:
#             print("screenshot failed:", e)
#         return False

#     img = np.array(screenshot)  # shape (h, w, 3) in RGB
#     if img.size == 0:
#         return False

#     # optional downscale to speed up
#     if downscale > 1:
#         new_w = max(1, img.shape[1] // downscale)
#         new_h = max(1, img.shape[0] // downscale)
#         img = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)

#     # METHOD A: saturation in HSV (OpenCV: H,S,V; S in 0-255)
#     hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
#     sat = hsv[..., 1]
#     low_sat_mask = (sat < sat_thresh)
#     low_sat_frac = float(np.mean(low_sat_mask))

#     # METHOD B: RGB max-min (nếu R,G,B rất gần nhau => grayscale)
#     rgb = img.astype(np.int16)
#     diff = rgb.max(axis=2) - rgb.min(axis=2)
#     low_diff_mask = (diff < diff_thresh)
#     low_diff_frac = float(np.mean(low_diff_mask))

#     # METHOD C (optional): color channel std across region (helpful for very flat images)
#     color_std = np.std(img.reshape(-1, 3), axis=0)  # std per channel
#     max_channel_std = float(np.max(color_std))

#     if debug:
#         print(f"region={region} downscale={downscale} sat_mean={sat.mean():.1f} low_sat_frac={low_sat_frac:.3f} "
#               f"low_diff_frac={low_diff_frac:.3f} max_channel_std={max_channel_std:.2f}")

    
#     return (low_sat_frac >= frac_thresh) and (low_diff_frac >= frac_thresh)

# check_open_icon = False
mark = {}
reg_clicked = None
reg_old = None
list_reg = []
cnt_mark = 0
while True:
    track = False
    gagoy_loc = safe_locate("images/gagoy.png", confidence=0.45)
    if gagoy_loc: 
        pag.click(gagoy_loc)
        time.sleep(random.uniform(0.5, 1))
        continue

    cnt_rw = 0

    # collect ticket
    collect_ticket_loc = safe_locate("images/collect_ticket.png", confidence=0.7)
    if collect_ticket_loc:
        # check_open_icon = True
        exit_loc = safe_locate("images/exit.png", confidence=0.7)
        if exit_loc :
            pag.click(exit_loc)
            time.sleep(random.uniform(0.2,0.5))
        
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


        time.sleep(random.uniform(0.5,1))

        his_loc = safe_locate("images/history.png", confidence=0.7)
        if his_loc:
            pag.moveTo(his_loc)
            time_rand = random.uniform(0.3, 0.5) 
            time.sleep(time_rand)
            pag.mouseDown()
            time_rand = random.uniform(0.2, 0.3) 
            time.sleep(time_rand)
            pag.moveRel(-1500, 0, duration=0.5)  
            pag.mouseUp()
        else:
            print("Không thấy history")
        
        
        time.sleep(random.uniform(0.3,0.6))

        
        favorite_loc = safe_locate("images/favorite.png", confidence=0.7)
        if favorite_loc:
            x, y = favorite_loc.left, favorite_loc.top
            dx, dy = 250, 650
            click_x = int(x + dx)
            click_y = int(y + dy)
            time.sleep(0.6) 
            pag.click(click_x, click_y)
    

    # scroll 
    full_attack_loc = safe_locate("images/full_attack.png", confidence=0.55)
    if full_attack_loc:
        screen_width, screen_height = pag.size()
        center_x, center_y = screen_width // 2, screen_height // 2
        pag.moveTo(center_x, center_y, duration=0.3)
        pag.dragRel(0, -300, duration=0.5, button='left')  
        

    # find attack and click
    attack_locs = safe_Alocate("images/attack.png", confidence=0.4)
    # loc_attack = None
    # if not attack_locs:
    #     continue
    if attack_locs:
        raw_boxes = [(int(l.left), int(l.top), int(l.width), int(l.height), l) for l in attack_locs]

        iou_threshold = 0.45   
        unique = deduplicate_boxes(raw_boxes, iou_thresh=iou_threshold)

        top_n = 10
        unique = unique[:top_n]

        for (x, y, w, h, loc) in unique:
            region = (x, y, w, h)
            if region not in mark:
                mark[region] = False
            if not is_gray_region(region) and mark[region]==False:
                pag.click(region)
                reg_clicked = region
                time.sleep(random.uniform(0.7, 1)) 
                cnt_mark +=1
                break    
            if mark[region] == True and cnt_mark >=5:
                mark[region] = False
                cnt_mark = 0       

        
    comeback_loc = safe_locate("images/comeback.png", confidence=0.7)
    while comeback_loc :
        mark[reg_clicked] = True
        comeback_pos = comeback_loc.left, comeback_loc.top, 450, 450
        pag.click(comeback_pos)
        exit_loc = wait_for_image("images/exit.png", timeout=5, confidence=0.7, interval=0.2)
        time.sleep(random.uniform(0.7,1))
        pag.click(exit_loc)
        comeback_loc = safe_locate("images/comeback.png", confidence=0.7)
        print(mark)
        continue
        # comeback_loc = safe_locate("images/comeback.png", confidence=0.7)
    # ready to attack
    ready_loc = safe_locate("images/ready.png", confidence=0.7)
    if ready_loc :
        time.sleep(random.uniform(1.3,1.6))
        pag.click(ready_loc)
        exit_loc = safe_locate("images/exit.png", confidence=0.7)
        # sequence of action
        while exit_loc:
            # click to friend
            time.sleep(1.5)
            pag.click(exit_loc)    
            
            friend_loc = wait_for_image("images/friend.png", timeout=5, confidence=0.7, interval=0.2)
            if friend_loc:
                pag.click(friend_loc)
                time.sleep(random.uniform(1,1.3))
                
            gift_loc = wait_for_image("images/gift.png", timeout=5, confidence=0.7, interval=0.2)
            if gift_loc:
                pag.click(gift_loc)
                time.sleep(random.uniform(1,1.3))
                
            ticket_loc = wait_for_image("images/ticket.png", timeout=5, confidence=0.7, interval=0.2)
            if ticket_loc:
                pag.click(ticket_loc)
                time.sleep(random.uniform(1,1.3))
                
            exit_loc = wait_for_image("images/exit.png", timeout=5, confidence=0.7, interval=0.2)
            if exit_loc:
                pag.click(exit_loc)
                time.sleep(1.6)
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
        time.sleep(0.6)  
        pag.click(click_x, click_y)
        time.sleep(random.uniform(1,1.3))  
        
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
    