import os
import sys
import random
import time
import pygame as pg

# ====== 定数 ======
WIDTH, HEIGHT = 1100, 650
DELTA = {
    pg.K_UP:    (0, -5),
    pg.K_DOWN:  (0,  5),
    pg.K_LEFT:  (-5, 0),
    pg.K_RIGHT: (5,  0),
}

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# ====== 関数群 ======
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
    for r in range(1, 11):  # 半径 10*r
        surf = pg.Surface((20*r, 20*r))
        pg.draw.circle(surf, (255, 0, 0), (10*r, 10*r), 10*r)
        surf.set_colorkey((0, 0, 0))
        bb_imgs.append(surf)
    bb_accs = [a for a in range(1, 11)]  # 1..10
    return bb_imgs, bb_accs


# ====== メイン ======
def main():
    pg.display.set_caption("逃げろ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))

    # 背景・こうかとん
    bg_img = pg.image.load("fig/pg_bg.jpg")
    kk_img = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)
    kk_rct = kk_img.get_rect(center=(300, 220))

    # 爆弾：サイズ・加速度の準備
    bb_imgs, bb_accs = init_bb_imgs()
    bb_idx = 0  # 現在の段階インデックス(0..9)
    bb_img = bb_imgs[bb_idx]
    bb_rct = bb_img.get_rect(
        center=(random.randint(0, WIDTH), random.randint(0, HEIGHT))
    )

    vx, vy = +5, +5  # 基本速度（向き）
    clock = pg.time.Clock()
    tmr = 0

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return

        screen.blit(bg_img, (0, 0))

        # === こうかとん操作 ===
        key_lst = pg.key.get_pressed()
        sum_mv = [0, 0]
        for key, mv in DELTA.items():
            if key_lst[key]:
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]

        kk_rct.move_ip(sum_mv)
        if check_bound(kk_rct) != (True, True):
            kk_rct.move_ip(-sum_mv[0], -sum_mv[1])
        screen.blit(kk_img, kk_rct)

        # === 時間で爆弾拡大＆加速 ===
        bb_idx = min(tmr // 500, 9)  # 0～9 に丸める
        # 画像サイズが変わるときは rect を中心維持で作り直し
        if bb_img is not bb_imgs[bb_idx]:
            center = bb_rct.center
            bb_img = bb_imgs[bb_idx]
            bb_rct = bb_img.get_rect(center=center)

        # 加速度で速度スケール
        avx = vx * bb_accs[bb_idx]
        avy = vy * bb_accs[bb_idx]

        # 移動と反射
        bb_rct.move_ip(avx, avy)
        yoko, tate = check_bound(bb_rct)
        if not yoko:
            vx *= -1
        if not tate:
            vy *= -1

        screen.blit(bb_img, bb_rct)

        # === 衝突判定（当たったら Game Over 表示して終了） ===
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
