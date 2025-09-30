import os
import sys
import random
import time
import pygame as pg


WIDTH, HEIGHT = 1100, 650
DELTA = {
    pg.K_UP:    (0, -5),
    pg.K_DOWN:  (0,  5),
    pg.K_LEFT:  (-5, 0),
    pg.K_RIGHT: (5,  0),
}


os.chdir(os.path.dirname(os.path.abspath(__file__)))


def check_bound(rct: pg.Rect) -> tuple[bool, bool]:
    """画面内なら True, はみ出す方向は False を返す (yoko, tate)"""
    yoko, tate = True, True
    if rct.left < 0 or rct.right > WIDTH:
        yoko = False
    if rct.top < 0 or rct.bottom > HEIGHT:
        tate = False
    return yoko, tate


def gameover(screen: pg.Surface) -> None:
    
    overlay = pg.Surface(screen.get_size())
    overlay.fill((0, 0, 0))
    overlay.set_alpha(200)

    font = pg.font.Font(None, 100)
    text = font.render("Game Over", True, (255, 255, 255))
    text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))

    
    base = pg.image.load("fig/8.png").convert_alpha()
    base = pg.transform.rotozoom(base, 0, 2.0)
    flipped = pg.transform.flip(base, True, False)

    gap = 40  
    left_rect = base.get_rect()
    left_rect.centery = HEIGHT // 2
    left_rect.right   = text_rect.left - gap

    right_rect = flipped.get_rect()
    right_rect.centery = HEIGHT // 2
    right_rect.left    = text_rect.right + gap

    
    screen.blit(overlay, (0, 0))
    screen.blit(base, left_rect)
    screen.blit(flipped, right_rect)
    screen.blit(text, text_rect)
    pg.display.update()
    time.sleep(5)


def init_bb_imgs() -> tuple[list[pg.Surface], list[int]]:
    
    bb_imgs: list[pg.Surface] = []
    for r in range(1, 11):                 
        surf = pg.Surface((20 * r, 20 * r))
        pg.draw.circle(surf, (255, 0, 0), (10 * r, 10 * r), 10 * r)
        surf.set_colorkey((0, 0, 0))
        bb_imgs.append(surf)
    bb_accs = [a for a in range(1, 11)]    
    return bb_imgs, bb_accs


def get_kk_imgs() -> dict[tuple[int, int], pg.Surface]:
    
    base = pg.image.load("fig/3.png").convert_alpha()
    scale = 0.9
    imgs = {
        (0,  0):  pg.transform.rotozoom(base,   0, scale),   
        (0, -5):  pg.transform.rotozoom(base,   0, scale),   
        (0,  5):  pg.transform.rotozoom(base, 180, scale),   
        (-5, 0):  pg.transform.rotozoom(base,  90, scale),   
        (5,  0):  pg.transform.rotozoom(base, -90, scale),   
        (-5, -5): pg.transform.rotozoom(base,  45, scale),   
        (5, -5):  pg.transform.rotozoom(base, -45, scale),   
        (-5, 5):  pg.transform.rotozoom(base, 135, scale),   
        (5,  5):  pg.transform.rotozoom(base, -135, scale),  
    }
    return imgs


def calc_orientation(org: pg.Rect, dst: pg.Rect,
                     current_xy: tuple[float, float]) -> tuple[float, float]:
    
    dx = dst.centerx - org.centerx
    dy = dst.centery - org.centery
    dist = (dx*dx + dy*dy) ** 0.5
    if dist == 0:
        return current_xy
    if dist < 300:
        return current_xy
    return (5 * dx / dist, 5 * dy / dist)   



def main():
    pg.display.set_caption("逃げろ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))

    
    bg_img = pg.image.load("fig/pg_bg.jpg").convert()

    
    kk_imgs = get_kk_imgs()
    kk_img = kk_imgs[(0, 0)]
    kk_rct = kk_img.get_rect(center=(300, 220))

    
    bb_imgs, bb_accs = init_bb_imgs()
    bb_idx = 0
    bb_img = bb_imgs[bb_idx]
    bb_rct = bb_img.get_rect(center=(random.randint(0, WIDTH), random.randint(0, HEIGHT)))

    
    dir_xy: tuple[float, float] = (5.0, 5.0)

    clock = pg.time.Clock()
    tmr = 0

    while True:
       
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return

        
        screen.blit(bg_img, (0, 0))

        
        key_lst = pg.key.get_pressed()
        sum_mv = [0, 0]
        for key, mv in DELTA.items():
            if key_lst[key]:
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]

        kk_rct.move_ip(sum_mv)
        if check_bound(kk_rct) != (True, True):
            kk_rct.move_ip(-sum_mv[0], -sum_mv[1])

        
        new_img = kk_imgs.get(tuple(sum_mv), kk_imgs[(0, 0)])
        if new_img is not kk_img:
            center = kk_rct.center
            kk_img = new_img
            kk_rct = kk_img.get_rect(center=center)
        screen.blit(kk_img, kk_rct)

        
        bb_idx = min(tmr // 500, 9)  
        if bb_img is not bb_imgs[bb_idx]:
            center = bb_rct.center
            bb_img = bb_imgs[bb_idx]
            bb_rct = bb_img.get_rect(center=center)

        
        dir_xy = calc_orientation(bb_rct, kk_rct, dir_xy)

        
        avx = dir_xy[0] * bb_accs[bb_idx]
        avy = dir_xy[1] * bb_accs[bb_idx]

        
        bb_rct.move_ip(avx, avy)
        yoko, tate = check_bound(bb_rct)
        if not yoko:
            dir_xy = (-dir_xy[0], dir_xy[1])
        if not tate:
            dir_xy = (dir_xy[0], -dir_xy[1])

        screen.blit(bb_img, bb_rct)

        
        if kk_rct.colliderect(bb_rct):
            gameover(screen)
            return

        pg.display.update()
        tmr += 1
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
