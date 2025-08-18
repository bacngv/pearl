import pyautogui as pag
import time 
import cv2
import pyscreeze
import random
import numpy as np

def wait_for_image(img, timeout=10, interval=0.3, confidence=0.5, region=None):
    """Chờ cho đến khi hình ảnh xuất hiện trên màn hình - tối ưu thời gian"""
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

def wait_for_any_image(images, timeout=10, interval=0.3, confidence=0.5, region=None):
    """Chờ cho đến khi một trong các hình ảnh xuất hiện - tối ưu thời gian"""
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
    # Chờ giao diện ổn định - giảm thời gian
    time.sleep(2.5)
    
    # Tìm và click friend.png
    img_trophies = 'images/friend.png'
    trophies_loc = wait_for_image(img_trophies, timeout=3, confidence=0.7)
    if not trophies_loc:
        print("Không thấy friend.png")
        return False, None, None
    
    time_rand = random.uniform(0.2, 0.4)  # Giảm thời gian random
    time.sleep(time_rand)
    pag.click(trophies_loc)
    
    # Chờ trang friend load xong bằng cách đợi center.png xuất hiện
    center_img = 'images/center.png'
    center_loc = wait_for_image(center_img, timeout=3, confidence=0.7)
    if center_loc:
        center = pag.center(center_loc)
        pag.moveTo(center)
        time_rand = random.uniform(0.3, 0.5)  # Giảm thời gian
        time.sleep(time_rand)
        pag.mouseDown()
        time_rand = random.uniform(0.2, 0.3)  # Giảm thời gian
        time.sleep(time_rand)
        pag.moveRel(-600, 0, duration=0.3)  # Giảm duration
        pag.mouseUp()
    else:
        print("Không thấy center.png, tiếp tục...")

    # Chờ sau khi swipe - giảm thời gian
    time.sleep(0.5)

    # Tìm và swipe leaderboard
    img_leaderboard = 'images/leaderboard.png'
    leaderboard_loc = wait_for_image(img_leaderboard, timeout=2, confidence=0.7)
    if leaderboard_loc:
        pag.moveTo(leaderboard_loc)
        time_rand = random.uniform(0.3, 0.5)  # Giảm thời gian
        time.sleep(time_rand)
        pag.mouseDown()
        time_rand = random.uniform(0.2, 0.3)  # Giảm thời gian
        time.sleep(time_rand)
        pag.moveRel(-1000, 0, duration=0.3)  # Giảm duration
        pag.mouseUp()
    else:
        print("Không thấy leaderboard.png")
    
    # Chờ sau khi swipe leaderboard - giảm thời gian
    time.sleep(0.5)

    # Tìm favorite và click vào vị trí tương đối
    favorite = 'images/favorite.png'
    favorite_loc = wait_for_image(favorite, timeout=2, confidence=0.7)
    if favorite_loc:
        x, y = favorite_loc.left, favorite_loc.top
        dx, dy = 200, 600
        click_x = int(x + dx)
        click_y = int(y + dy)
        time.sleep(0.5)  # Giảm thời gian
        pag.click(click_x, click_y)

    # Chờ trang attack load xong - giảm thời gian
    time.sleep(1)
    
    time.sleep(1)

    # Tìm attack button không bị gray
    img_attack = 'images/attack.png'
    conf = 0.7
    ok = False
    loc_attack = None

    start_time = time.time()
    timeout_attack = 6.0  # tổng thời gian tối đa (giây) để tìm button

    while time.time() - start_time < timeout_attack:
        try:
            # locateAllOnScreen có thể ném pyscreeze.ImageNotFoundException
            attack_locs = list(pag.locateAllOnScreen(img_attack, confidence=conf))
        except pyscreeze.ImageNotFoundException:
            # không tìm thấy kết quả (an toàn tiếp tục)
            attack_locs = []
        except Exception as e:
            # bắt chung để tránh crash; log để debug nếu cần
            print("Lỗi khi locateAllOnScreen:", e)
            attack_locs = []

        if not attack_locs:
            # không tìm thấy ở mức confidence hiện tại -> giảm confidence / chờ
            print(f"Không thấy {img_attack} với confidence={conf:.2f}")
            # giảm confidence từng bước nhỏ, nhưng không thấp hơn 0.5
            if conf > 0.5:
                conf = round(max(0.5, conf - 0.02), 2)
                print(f"Giảm confidence xuống {conf:.2f} và thử lại")
            time.sleep(0.25)
            continue

        # có một số vị trí, kiểm tra vùng non-gray
        for loc in attack_locs:
            region = (int(loc.left), int(loc.top), int(loc.width), int(loc.height))
            if not is_gray_region(region):
                loc_attack = loc
                ok = True
                print(f"Tìm thấy non-gray tại {loc} với confidence={conf:.2f}")
                break

        if ok:
            break
        else:
            # tất cả vùng là gray -> giảm confidence 1 bước và thử lại
            print(f"Tất cả vùng là gray tại confidence={conf:.2f} -> giảm và thử lại")
            if conf > 0.5:
                conf = round(max(0.5, conf - 0.1), 2)
            time.sleep(0.25)

    # sau timeout: nếu vẫn không ok -> trả về thất bại an toàn
    if not ok:
        print("Không tìm thấy attack non-gray sau timeout, thoát access()")
        return False, None, None

    return ok, conf, loc_attack


def doattack():
    # Chờ trận đấu bắt đầu - giảm thời gian
    time.sleep(1.5)
    
    knight = 'images/knight.png'
    end = 'images/end.png'
    reward = 'images/reward.png'
    flag = False
    done = False
    
    while not done:
        # Kiểm tra xem có end button không
        end_loc = wait_for_image(end, timeout=0.5, confidence=0.7, interval=0.2)
        if end_loc:
            print("trạng thái end!")
        
        # Nếu chưa có end button, tìm và click knight
        if not end_loc:
            knight_loc = wait_for_image(knight, timeout=0.5, confidence=0.4, interval=0.2)
            if knight_loc:
                pag.click(knight_loc)
                flag = True
            continue
        
        # Nếu đã có flag (đã click knight) và có end button
        if flag and end_loc:
            print("Click kết thúc")
            for _ in range(10):
                end_loc = wait_for_image(end, timeout=0.5, confidence=0.7, interval=0.2)
                time.sleep(0.2)
                pag.click(end_loc)
            # pag.click(end_loc)
            # time.sleep(0.5)  # Giảm thời gian
            # pag.click(end_loc)
            
            # Chờ màn hình kết quả xuất hiện - giảm thời gian
            time.sleep(1)
            rw=0
            rw_list = []
            while not done:
                # Tìm sell button
                sell_loc = wait_for_image("images/sell.png", timeout=2, confidence=0.7, interval=0.5)
                if sell_loc:
                    print("tìm thấy sell")
                    pag.click(sell_loc)
                    for _ in range(3):
                        time.sleep(0.3)
                        pag.click(sell_loc)
                    time.sleep(1)  # Giảm thời gian
                    continue
                
                # Nếu không có sell, tìm giveup
                giveup_loc = wait_for_image("images/giveup.png", timeout=2, confidence=0.7, interval=0.2)
                if giveup_loc:
                    x, y = giveup_loc.left, giveup_loc.top
                    dx, dy = 120, 160
                    click_x = x + dx
                    click_y = y + dy
                    time.sleep(0.5)  # Giảm thời gian
                    pag.click(click_x, click_y)
                    time.sleep(1)  # Giảm thời gian
                    
                    # Click liên tục để skip - tối ưu
                    n_clicks = 10
                    total_time = 2.5  # Giảm từ 3 xuống 1.5
                    delay = total_time / n_clicks
                    for _ in range(n_clicks):
                        pag.click(click_x, click_y)
                        time.sleep(delay)
                    continue
                
                # Nếu không có giveup, tìm reward
                reward_loc = wait_for_image("images/reward.png", timeout=5, confidence=0.7, interval=0.2)
                if reward_loc:
                    pag.click(reward_loc)
                    if reward_loc not in rw_list:
                        rw_list.append(reward_loc)
                    time.sleep(1)  # Giảm thời gian
                    if len(rw_list) == 6:
                        break
                    continue
                
                # Nếu không tìm thấy gì, click để skip và kết thúc - tối ưu
                n_clicks = 10  # Giảm số click
                total_time = 2.5  # Giảm thời gian
                delay = total_time / n_clicks
                try:
                    for _ in range(n_clicks):
                        pag.click(click_x, click_y)
                        time.sleep(delay)
                except:
                    # Nếu click_x, click_y chưa được định nghĩa
                    pass
                
                done = True
                time.sleep(1)  # Giảm thời gian

        time_random = random.uniform(0.1, 0.3)  # Giảm thời gian random
        for _ in range(10):
            time.sleep(0.2)
            pag.click(sell_loc)
        time.sleep(time_random)

if __name__ == "__main__":
    ok = True
    while ok:
        ok, conf, loc_attack = access()
        if not ok:
            print('hết nhà để đánh')
            break
            
        # Click vào attack button - giảm thời gian random
        time_rand = random.uniform(0.5, 1)  # Giảm từ 1.5-3 xuống 0.5-1
        time.sleep(time_rand)
        pag.click(loc_attack)
        
        
        # Nếu không có comeback, chờ ready button - giảm thời gian
        time.sleep(1.5)
        ready = 'images/ready.png'
        ready_loc = wait_for_image(ready, timeout=3, confidence=0.7, interval=0.2)
        if ready_loc:
            n_clicks = 15  # Giảm số click
            total_time = 2.5  # Giảm thời gian
            delay = total_time / n_clicks
            for _ in range(n_clicks):
                time.sleep(delay)
                pag.click(ready_loc)
            
            comeback_loc = wait_for_image("images/comeback.png", timeout=2, confidence=0.7, interval=0.2)

            if comeback_loc:
                pag.click(comeback_loc)
                
                # Chờ và tìm exit button
                exit_loc = wait_for_image("images/exit.png", timeout=3, confidence=0.7, interval=0.2)
                if exit_loc:
                    pag.click(exit_loc)
                    time.sleep(0.5)  # Giảm thời gian
                    continue
            
            # Chờ và kiểm tra lack bread - giảm thời gian
            time.sleep(1)
            lack_bread = 'images/lackbread.png'
            lack_bread_loc = wait_for_image(lack_bread, timeout=2, confidence=0.7, interval=0.2)
            
            makefull_loc = wait_for_image("images/makefull.png", timeout=3, confidence=0.7, interval=0.2)
            if makefull_loc:
                print("thu thập bánh")
                pag.click(makefull_loc)
            else :
                if lack_bread_loc:
                    # Nếu thiếu bread, quay về friend để lấy ticket
                    exit_loc = wait_for_image("images/exit.png", timeout=3, confidence=0.7, interval=0.2)
                    if exit_loc:
                        pag.click(exit_loc)
                        
                    # Chờ và click friend
                    friend_loc = wait_for_image("images/friend.png", timeout=5, confidence=0.7, interval=0.2)
                    if friend_loc:
                        pag.click(friend_loc)
                        
                    # Chờ và click gift
                    gift_loc = wait_for_image("images/gift.png", timeout=3, confidence=0.7, interval=0.2)
                    if gift_loc:
                        pag.click(gift_loc)
                        
                    # Chờ và click ticket
                    ticket_loc = wait_for_image("images/ticket.png", timeout=3, confidence=0.7, interval=0.2)
                    if ticket_loc:
                        pag.click(ticket_loc)
                        
                    # Chờ và thoát
                    exit_loc = wait_for_image("images/exit.png", timeout=3, confidence=0.7, interval=0.2)
                    if exit_loc:
                        pag.click(exit_loc)
                        time.sleep(0.5)  # Giảm thời gian
                else:
                    # Nếu không thiếu bread, bắt đầu attack
                    # time.sleep(2)
                    doattack()