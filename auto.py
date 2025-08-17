import pyautogui as pag
import time 
import cv2
import random
import numpy as np

def wait_for_image(img, timeout=10, interval=0.8, confidence=0.5, region=None):
    """Chờ cho đến khi hình ảnh xuất hiện trên màn hình"""
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

def wait_for_any_image(images, timeout=10, interval=0.8, confidence=0.5, region=None):
    """Chờ cho đến khi một trong các hình ảnh xuất hiện"""
    start = time.time()
    while time.time() - start < timeout:
        for img in images:
            try:
                loc = pag.locateOnScreen(img, confidence=confidence, region=region)
                if loc:
                    return img, loc
            except pag.ImageNotFoundException:
                pass
        time.sleep(interval)
    return None, None

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

def access():
    # Chờ giao diện ổn định
    time.sleep(1)
    
    # Tìm và click friend.png
    img_trophies = 'images/friend.png'
    trophies_loc = wait_for_image(img_trophies, timeout=5, confidence=0.7)
    if not trophies_loc:
        print("Không thấy friend.png")
        return False, None, None
    
    time_rand = random.uniform(0.5, 1)
    time.sleep(time_rand)
    pag.click(trophies_loc)
    
    # Chờ trang friend load xong bằng cách đợi center.png xuất hiện
    center_img = 'images/center.png'
    center_loc = wait_for_image(center_img, timeout=5, confidence=0.7)
    if center_loc:
        center = pag.center(center_loc)
        pag.moveTo(center)
        time_rand = random.uniform(0.7, 1)
        time.sleep(time_rand)
        pag.mouseDown()
        time_rand = random.uniform(0.3, 0.5)
        time.sleep(time_rand)
        pag.moveRel(-600, 0, duration=0.5)
        pag.mouseUp()
    else:
        print("Không thấy center.png, tiếp tục...")

    # Chờ sau khi swipe
    time.sleep(1)

    # Tìm và swipe leaderboard
    img_leaderboard = 'images/leaderboard.png'
    leaderboard_loc = wait_for_image(img_leaderboard, timeout=3, confidence=0.7)
    if leaderboard_loc:
        pag.moveTo(leaderboard_loc)
        time_rand = random.uniform(0.7, 1)
        time.sleep(time_rand)
        pag.mouseDown()
        time_rand = random.uniform(0.3, 0.5)
        time.sleep(time_rand)
        pag.moveRel(-1000, 0, duration=0.5)
        pag.mouseUp()
    else:
        print("Không thấy leaderboard.png")
    
    # Chờ sau khi swipe leaderboard
    time.sleep(1)

    # Tìm favorite và click vào vị trí tương đối
    favorite = 'images/favorite.png'
    favorite_loc = wait_for_image(favorite, timeout=3, confidence=0.7)
    if favorite_loc:
        x, y = favorite_loc.left, favorite_loc.top
        dx, dy = 200, 600
        click_x = int(x + dx)
        click_y = int(y + dy)
        time.sleep(1)
        pag.click(click_x, click_y)

    # Chờ trang attack load xong
    time.sleep(2)
    
    # Tìm attack button không bị gray
    img_attack = 'images/attack.png'
    conf = 0.9
    ok = False
    loc_attack = None

    while conf >= 0.3:
        attack_locs = list(pag.locateAllOnScreen(img_attack, confidence=conf))
        if not attack_locs:
            print(f"Không thấy {img_attack} với confidence={conf}, giảm xuống {conf-0.1:.1f}")
            conf -= 0.1
            continue

        for loc in attack_locs:
            region = (int(loc.left), int(loc.top), int(loc.width), int(loc.height))
            if not is_gray_region(region):
                loc_attack = loc
                ok = True
                print(f"Tìm thấy non-gray tại {loc} với confidence={conf}")
                break
        if ok:
            break
        else:
            print(f"Tất cả vùng là gray với confidence={conf}, giảm xuống {conf-0.1:.1f}")
            conf -= 0.1

    return ok, conf, loc_attack

def doattack():
    # Chờ trận đấu bắt đầu
    time.sleep(3)
    
    knight = 'images/knight.png'
    end = 'images/end.png'
    reward = 'images/reward.png'
    flag = False
    done = False
    
    while not done:
        # Kiểm tra xem có end button không
        end_loc = wait_for_image(end, timeout=1, confidence=0.7)
        if end_loc:
            print("trạng thái end!")
        
        # Nếu chưa có end button, tìm và click knight
        if not end_loc:
            knight_loc = wait_for_image(knight, timeout=1, confidence=0.5)
            if knight_loc:
                pag.click(knight_loc)
                flag = True
            continue
        
        # Nếu đã có flag (đã click knight) và có end button
        if flag and end_loc:
            print("Click kết thúc")
            pag.click(end_loc)
            time.sleep(1)
            pag.click(end_loc)
            
            # Chờ màn hình kết quả xuất hiện
            time.sleep(2)
            
            while not done:
                # Tìm sell button
                sell_loc = wait_for_image("images/sell.png", timeout=2, confidence=0.6)
                if sell_loc:
                    pag.click(sell_loc)
                    time.sleep(2)
                    continue
                
                # Nếu không có sell, tìm giveup
                giveup_loc = wait_for_image("images/giveup.png", timeout=2, confidence=0.4)
                if giveup_loc:
                    x, y = giveup_loc.left, giveup_loc.top
                    dx, dy = 120, 160
                    click_x = x + dx
                    click_y = y + dy
                    time.sleep(1)
                    pag.click(click_x, click_y)
                    time.sleep(2)
                    
                    # Click liên tục để skip
                    n_clicks = 10
                    total_time = 3
                    delay = total_time / n_clicks
                    for _ in range(n_clicks):
                        pag.click(click_x, click_y)
                        time.sleep(delay)
                    continue
                
                # Nếu không có giveup, tìm reward
                reward_loc = wait_for_image("images/reward.png", timeout=5, confidence=0.7)
                if reward_loc:
                    pag.click(reward_loc)
                    time.sleep(2)
                    continue
                
                # Nếu không tìm thấy gì, click để skip và kết thúc
                n_clicks = 10
                total_time = 3
                delay = total_time / n_clicks
                try:
                    for _ in range(n_clicks):
                        pag.click(click_x, click_y)
                        time.sleep(delay)
                except:
                    # Nếu click_x, click_y chưa được định nghĩa
                    pass
                
                done = True
                time.sleep(3)

        time_random = random.uniform(0.2, 0.5)
        time.sleep(time_random)

if __name__ == "__main__":
    ok = True
    while ok:
        ok, conf, loc_attack = access()
        if not ok:
            print('hết nhà để đánh')
            break
            
        # Click vào attack button
        time_rand = random.uniform(1.5, 3)
        time.sleep(time_rand)
        pag.click(loc_attack)
        
        # Kiểm tra comeback button (có thể là do đã attack rồi)
        comeback_loc = wait_for_image("images/comeback.png", timeout=3, confidence=0.7)
        if comeback_loc:
            pag.click(comeback_loc)
            
            # Chờ và tìm exit button
            exit_loc = wait_for_image("images/exit.png", timeout=5, confidence=0.7)
            if exit_loc:
                pag.click(exit_loc)
                time.sleep(1)
                continue
        
        # Nếu không có comeback, chờ ready button
        time.sleep(3)
        ready = 'images/ready.png'
        ready_loc = wait_for_image(ready, timeout=5, confidence=0.7)
        if ready_loc:
            pag.click(ready_loc)
            
            # Chờ và kiểm tra lack bread
            time.sleep(2)
            lack_bread = 'images/lackbread.png'
            lack_bread_loc = wait_for_image(lack_bread, timeout=3, confidence=0.7)
            
            if lack_bread_loc:
                # Nếu thiếu bread, quay về friend để lấy ticket
                exit_loc = wait_for_image("images/exit.png", timeout=3, confidence=0.7)
                if exit_loc:
                    pag.click(exit_loc)
                    
                # Chờ và click friend
                friend_loc = wait_for_image("images/friend.png", timeout=5, confidence=0.7)
                if friend_loc:
                    pag.click(friend_loc)
                    
                # Chờ và click gift
                gift_loc = wait_for_image("images/gift.png", timeout=5, confidence=0.7)
                if gift_loc:
                    pag.click(gift_loc)
                    
                # Chờ và click ticket
                ticket_loc = wait_for_image("images/ticket.png", timeout=5, confidence=0.7)
                if ticket_loc:
                    pag.click(ticket_loc)
                    
                # Chờ và thoát
                exit_loc = wait_for_image("images/exit.png", timeout=5, confidence=0.7)
                if exit_loc:
                    pag.click(exit_loc)
                    time.sleep(1)
            else:
                # Nếu không thiếu bread, bắt đầu attack
                doattack()