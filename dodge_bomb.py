import os
import sys
import random
import time
import pygame as pg

# ===== 定数 =====
WIDTH, HEIGHT = 1100, 650
DELTA = {                      # キー→移動量
    pg.K_UP:    (0, -5),
    pg.K_DOWN:  (0,  5),
    pg.K_LEFT:  (-5, 0),
    pg.K_RIGHT: (5,  0),
}

# このファイルの場所を作業ディレクトリに
#os.chdir(os.path.dirname(os.path.abspath(__file__)))

# ===== 共通関数 =====
def check_bound(rct: pg.Rect) -> tuple[bool, bool]:
    """画面内なら True, はみ出す方向は False を返す (yoko, tate)"""
    yoko, tate = True, True
    if rct.left < 0 or rct.right > WIDTH:
        yoko = False
    if rct.top < 0 or rct.bottom > HEIGHT:
        tate = False
    return yoko, tate


def gameover(screen: pg.Surface) -> None:
    """暗転 + 'Game Over' + 泣きこうかとん を5秒表示"""
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


def init_bb_imgs() -> tuple[list[pg.Surface], list[int]]:
    """爆弾のサイズ(10段階)と加速度(1～10)のリストを返す"""
    bb_imgs: list[pg.Surface] = []
    for r in range(1, 11):                 # 半径: 10*r
        surf = pg.Surface((20*r, 20*r))
        pg.draw.circle(surf, (255, 0, 0), (10*r, 10*r), 10*r)
        surf.set_colorkey((0, 0, 0))
        bb_imgs.append(surf)
    bb_accs = [a for a in range(1, 11)]    # 1..10
    return bb_imgs, bb_accs


def get_kk_imgs() -> dict[tuple[int, int], pg.Surface]:
    """移動量(タプル)→こうかとん画像 の辞書を作る"""
    base = pg.image.load("fig/3.png")
    scale = 0.9
    imgs = {
        (0,  0):  pg.transform.rotozoom(base,   0, scale),   # 静止
        (0, -5):  pg.transform.rotozoom(base,   0, scale),   # 上
        (0,  5):  pg.transform.rotozoom(base, 180, scale),   # 下
        (-5, 0):  pg.transform.rotozoom(base,  90, scale),   # 左
        (5,  0):  pg.transform.rotozoom(base, -90, scale),   # 右
        (-5, -5): pg.transform.rotozoom(base,  45, scale),   # 左上
        (5, -5):  pg.transform.rotozoom(base, -45, scale),   # 右上
        (-5, 5):  pg.transform.rotozoom(base, 135, scale),   # 左下
        (5,  5):  pg.transform.rotozoom(base, -135, scale),  # 右下
    }
    return imgs


# ===== メイン =====
def main():
    pg.display.set_caption("逃げろ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))

    # 背景
    bg_img = pg.image.load("fig/pg_bg.jpg")

    # こうかとん（方向別画像）
    kk_imgs = get_kk_imgs()
    kk_img = kk_imgs[(0, 0)]
    kk_rct = kk_img.get_rect(center=(300, 220))

    # 爆弾：サイズ＆加速度の段階
    bb_imgs, bb_accs = init_bb_imgs()
    bb_idx = 0
    bb_img = bb_imgs[bb_idx]
    bb_rct = bb_img.get_rect(center=(random.randint(0, WIDTH), random.randint(0, HEIGHT)))

    vx, vy = +5, +5              # 爆弾の基準速度（向き）
    clock = pg.time.Clock()
    tmr = 0

    while True:
        # --- event ---
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return

        # --- draw background ---
        screen.blit(bg_img, (0, 0))

        # --- key input & move koukaton ---
        key_lst = pg.key.get_pressed()
        sum_mv = [0, 0]
        for key, mv in DELTA.items():
            if key_lst[key]:
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]

        kk_rct.move_ip(sum_mv)
        if check_bound(kk_rct) != (True, True):
            kk_rct.move_ip(-sum_mv[0], -sum_mv[1])

        # 方向に応じて画像切替（中心は維持）
        new_img = kk_imgs.get(tuple(sum_mv), kk_imgs[(0, 0)])
        if new_img is not kk_img:
            center = kk_rct.center
            kk_img = new_img
            kk_rct = kk_img.get_rect(center=center)

        screen.blit(kk_img, kk_rct)

        # --- bomb: grow & accelerate with time ---
        bb_idx = min(tmr // 500, 9)   # 0..9
        if bb_img is not bb_imgs[bb_idx]:
            center = bb_rct.center
            bb_img = bb_imgs[bb_idx]
            bb_rct = bb_img.get_rect(center=center)

        avx = vx * bb_accs[bb_idx]
        avy = vy * bb_accs[bb_idx]

        bb_rct.move_ip(avx, avy)
        yoko, tate = check_bound(bb_rct)
        if not yoko:
            vx *= -1
        if not tate:
            vy *= -1

        screen.blit(bb_img, bb_rct)

        # --- collision → game over ---
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
