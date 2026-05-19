import pygame as pg
import random
import sys
import os
import math

# --- 初期設定 ---
os.chdir(os.path.dirname(os.path.abspath(__file__)))
pg.init()

# 画面サイズ
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 400
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pg.display.set_caption("こうかとんランゲーム")

# カラー定義
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# フレームレート管理
clock = pg.time.Clock()
FPS = 60

# --- 画像の読み込み ---
try:
    player_run = pg.image.load("./fig/run.png").convert_alpha()
    
    # 障害物と背景
    obstacle_img = pg.image.load("./fig/alien.png").convert_alpha()
    bg_img = pg.image.load("./fig/pg_bg.jpg").convert()
    
    # 背景画像を画面サイズにフィットさせる
    bg_img = pg.transform.scale(bg_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
    
except pg.error as e:
    print(f"画像が見つかりません。フォルダ構成を確認してください: {e}")
    pg.quit()
    sys.exit()

# --- クラス定義 ---

class Player:
    """プレイヤー（こうかとん）のクラス"""
    def __init__(self):
        # 縦長の画像(約3:4)に合わせてサイズを横60px、高さ80pxに最適化
        self.width = 60
        self.height = 80
        
        # 画像をリサイズして保持
        self.img_run = pg.transform.scale(player_run, (self.width, self.height))
        
        self.x = 100
        self.y_floor = SCREEN_HEIGHT - 80 - self.height  # 地面の上のY座標
        self.y = self.y_floor
        
        # ジャンプ関連の物理パラメータ
        self.is_jumping = False
        self.jump_velocity = 15  # 初速度
        self.velocity_y = 0
        self.gravity = 0.75       # 重力

    def jump(self):
        if not self.is_jumping:
            self.is_jumping = True
            self.velocity_y = -self.jump_velocity

    def update(self):
        if self.is_jumping:
            self.y += self.velocity_y
            self.velocity_y += self.gravity  # 重力を加算
            
            # 着地判定
            if self.y >= self.y_floor:
                self.y = self.y_floor
                self.is_jumping = False
                self.velocity_y = 0

    def draw(self):
        # 正しい縦横比に修正された run.png を表示
        current_image = self.img_run
        screen.blit(current_image, (self.x, self.y))

    def get_rect(self):
        return pg.Rect(self.x, self.y, self.width, self.height)


class Obstacle:
    """障害物（エイリアン）のクラス"""
    def __init__(self, speed):
        # 画像サイズをゲーム用に調整
        self.width = 50
        self.height = 50
        self.image = pg.transform.scale(obstacle_img, (self.width, self.height))
        
        self.x = SCREEN_WIDTH
        self.y = SCREEN_HEIGHT - 80 - self.height
        self.speed = speed

    def update(self):
        self.x -= self.speed  # 左へ自動移動

    def draw(self):
        screen.blit(self.image, (self.x, self.y))

    def get_rect(self):
        return pg.Rect(self.x, self.y, self.width, self.height)


# --- メインゲームループ ---
def main():

    font = pg.font.SysFont("meiryo", 35)
    title_font = pg.font.SysFont("meiryo", 55)

    # ゲーム状態
    START = 0
    PLAYING = 1
    GAME_OVER = 2

    game_state = START

    # 初期化関数
    def reset_game():
        player = Player()
        obstacles = []
        score = 0
        game_speed = 7
        spawn_timer = 0
        next_spawn_time = random.randint(60,120)

        return (
            player,
            obstacles,
            score,
            game_speed,
            spawn_timer,
            next_spawn_time
        )

    player, obstacles, score, game_speed, spawn_timer, next_spawn_time = reset_game()

    title_anim = 0

    while True:

        # -------- イベント処理 --------
        for event in pg.event.get():

            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()

            if event.type == pg.KEYDOWN:

                if event.key == pg.K_SPACE:

                    # タイトル画面 → ゲーム開始
                    if game_state == START:
                        game_state = PLAYING

                    # プレイ中 → ジャンプ
                    elif game_state == PLAYING:
                        player.jump()

                    # ゲームオーバー → リスタート
                    elif game_state == GAME_OVER:
                        (
                            player,
                            obstacles,
                            score,
                            game_speed,
                            spawn_timer,
                            next_spawn_time
                        ) = reset_game()

                        game_state = PLAYING

        # タイトルアニメーション
        title_anim += 0.05

        # -------- 更新処理 --------
        if game_state == PLAYING:

            player.update()
            score += 1

            spawn_timer += 1

            if spawn_timer >= next_spawn_time:
                obstacles.append(Obstacle(game_speed))
                spawn_timer = 0
                next_spawn_time = random.randint(50,100)

            for obstacle in obstacles[:]:

                obstacle.update()

                if obstacle.x + obstacle.width < 0:
                    obstacles.remove(obstacle)

                if player.get_rect().colliderect(
                        obstacle.get_rect()):

                    game_state = GAME_OVER

        # -------- 描画処理 --------
        screen.blit(bg_img, (0,0))

        # ===== タイトル画面 =====
        if game_state == START:

            # 半透明黒背景
            dark_surface = pg.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            dark_surface.set_alpha(120)
            dark_surface.fill((0, 0, 0))
            screen.blit(dark_surface, (0, 0))

            # タイトル上下揺れ
            offset_y = int(math.sin(title_anim) * 10)

            title = title_font.render(
                "こうかとんランゲーム",
                True,
                WHITE
            )

            press = font.render(
                "SPACEキーでスタート",
                True,
                WHITE
            )

            title_rect = title.get_rect(
                center=(SCREEN_WIDTH // 2, 140 + offset_y)
            )

            press_rect = press.get_rect(
                center=(SCREEN_WIDTH // 2, 240)
            )

            screen.blit(title, title_rect)
            screen.blit(press, press_rect)

        # ===== プレイ中・ゲームオーバー =====
        else:

            # プレイヤー
            player.draw()

            # 障害物
            for obstacle in obstacles:
                obstacle.draw()

            # スコア
            score_text = font.render(
                f"Score: {score}",
                True,
                BLACK
            )

            screen.blit(score_text, (10,10))

        # ===== ゲームオーバー画面 =====
        if game_state == GAME_OVER:

            dark_surface = pg.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            dark_surface.set_alpha(120)
            dark_surface.fill((0,0,0))
            screen.blit(dark_surface, (0,0))

            over = title_font.render(
                "ゲームオーバー",
                True,
                WHITE
            )

            retry = font.render(
                "SPACEキーでリスタート",
                True,
                WHITE
            )

            score_result = font.render(
            f"スコア : {score}",
                True,
                WHITE
            )

            over_rect = over.get_rect(
                center=(SCREEN_WIDTH//2,140)
            )

            retry_rect = retry.get_rect(
                center=(SCREEN_WIDTH//2,220)
            )

            score_rect = score_result.get_rect(
                center=(SCREEN_WIDTH//2,280)
            )

            screen.blit(over, over_rect)
            screen.blit(retry, retry_rect)
            screen.blit(score_result, score_rect)

        pg.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()