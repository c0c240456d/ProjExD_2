import os
import sys
import random
import time
import pygame as pg

# ---------- 定数 ----------
WIDTH, HEIGHT = 1100, 650
DELTA = {
    pg.K_UP:    (0, -5),
    pg.K_DOWN:  (0,  5),
    pg.K_LEFT:  (-5, 0),
    pg.K_RIGHT: (5,  0),
}

# スクリプトの場所を作業ディレクトリに
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# ---------- 関数 ----------
def check_bound(rct: pg.Rect) -> tuple[bool, bool]:
    """画面内なら True, はみ出す方向は False を返す (yoko, tate)"""
    yoko, tate = True, True
    if rct.left < 0 or rct.right > WIDTH:
        yoko = False
    if rct.top < 0 or rct.bottom > HEIGHT:
        tate = False
    return yoko, tate


def gameover(screen: pg.Surface) -> None:
    """暗転＋『Game Over』＋泣きこうかとんを5秒表示"""
    overlay = pg.Surface(screen.get_size())
    overlay.set_alpha(200)
    overlay.fill((0, 0, 0))

    font = pg.font.Font(None, 100)
    text = font.render("Game Over", True, (255, 255, 255))
    text_rect = text.get_rect(center=(WIDTH/2, HEIGHT/2 - 60))

    cry = pg.image.load("fig/8.png")
    cry = pg.transform.rotozoom(cry, 0, 2.0)
    cry_rect = cry.get_rect(center=(WIDTH/2, HEIGHT/2 + 40))

    screen.blit(overlay, (0, 0))
    screen.blit(text, text_rect)
    screen.blit(cry, cry_rect)
    pg.display.update()
    time.sleep(5)


# ---------- メイン ----------
def main():
    pg.display.set_caption("逃げろ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))

    # 背景・こうかとん
    bg_img = pg.image.load("fig/pg_bg.jpg")
    kk_img = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)
    kk_rct = kk_img.get_rect()
    kk_rct.center = (300, 220)

    # 爆弾（赤い円を描いた Surface）
    bb_img = pg.Surface((20, 20))
    pg.draw.circle(bb_img, (255, 0, 0), (10, 10), 10)
    bb_img.set_colorkey((0, 0, 0))
    bb_rct = bb_img.get_rect()
    bb_rct.centerx = random.randint(0, WIDTH)
    bb_rct.centery = random.randint(0, HEIGHT)

    vx, vy = +5, +5
    clock = pg.time.Clock()

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return

        screen.blit(bg_img, (0, 0))

        # 衝突したらゲームオーバー表示して終了
        if kk_rct.colliderect(bb_rct):
            gameover(screen)
            return

        # キー入力
        key_lst = pg.key.get_pressed()
        sum_mv = [0, 0]
        for key, mv in DELTA.items():
            if key_lst[key]:
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]

        # こうかとん移動（はみ出したら差し戻し）
        kk_rct.move_ip(sum_mv)
        if check_bound(kk_rct) != (True, True):
            kk_rct.move_ip(-sum_mv[0], -sum_mv[1])

        screen.blit(kk_img, kk_rct)

        # 爆弾移動＆反射
        bb_rct.move_ip(vx, vy)
        yoko, tate = check_bound(bb_rct)
        if not yoko:
            vx *= -1
        if not tate:
            vy *= -1

        screen.blit(bb_img, bb_rct)

        pg.display.update()
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
