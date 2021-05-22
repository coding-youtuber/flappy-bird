# pygameを読み込む
import pygame
from pygame.locals import *
# 乱数を使うために読み込む
import random

# pygameを初期化
pygame.init()

# クロックのインスタンスを生成
clock = pygame.time.Clock()
# fpsを設定、ここでは1秒間に60フレームを描画
fps = 60

# ゲーム画面の横幅
screen_width = 864
# ゲーム画面の縦幅
screen_height = 936

# ゲーム画面を生成
screen = pygame.display.set_mode((screen_width, screen_height))

# ゲームのタイトル名を設定
pygame.display.set_caption("Flappy Bird")

# スコア表示の文字フォントを設定
font = pygame.font.SysFont("Bauhaus 93", 60)

# 文字の色を白色に設定
white = (255, 255, 255)

# 地面のスクロールを管理する変数
ground_scroll = 0
# スクロールの速さ
scroll_speed = 4
# 飛行中かどうかのフラグ
flying = False
# ゲームオーバーのフラグ
game_over = False
# 土管の間の距離
pipe_gap = 350
# 土管の頻度
pipe_frequency = 1500
# 最後の土管
last_pipe = pygame.time.get_ticks() - pipe_frequency
# スコア
score = 0
# 土管の通過フラグ
pass_pipe = False

# 背景、地面、リスタートボタンの画像をロード
bg = pygame.image.load("../img/bg.png")
ground_img = pygame.image.load("../img/ground.png")
buttom_img = pygame.image.load("../img/restart.png")

# 文字を描画する関数
def draw_text(text, font, text_col, x, y):
  img = font.render(text, True, text_col)
  screen.blit(img, (x, y))

def reset_game():
  """
  ゲームをリセットする

  鳥をスタートの位置に戻す
  スコアを0に戻す
  """
  pipe_group.empty()
  flappy.rect.x = 100
  flappy.rect.y = int(screen_width / 2)
  score = 0

  return score

class Bird(pygame.sprite.Sprite):
  """
  鳥クラス
  """
  def __init__(self, x, y):
    """
    初期化関数、インスタンス生成時に呼ばれる関数
    """
    pygame.sprite.Sprite.__init__(self)
    # 鳥の画像が入ったリスト
    self.images = []
    # 画像index
    self.index = 0
    # カウンター
    self.counter = 0

    # 3枚の画像をリストに入れる
    for num in range(1, 4):
      img = pygame.image.load(f"../img/bird{num}.png")
      self.images.append(img)

    # インデックスを用いて画像を取得
    self.image = self.images[self.index]
    # 画像を囲む四角形を取得
    self.rect = self.image.get_rect()
    # 画像を囲む四角形の中央を指定した座標位置にする
    self.rect.center = [x, y]
    # 速度
    self.vel = 0
    # クリックのフラグ
    self.clicked = False
  
  def update(self):
    """
    更新関数 フレーム毎に実行
    """

    # 飛行中なら
    if flying == True:
      # 速度が増加。つまり下に落ちる
      self.vel += 0.5
      # 速度が一定速度以上になったら
      if self.vel > 8:
        # 最高速度以上に速度はあがらない
        self.vel = 8

      # 鳥が地面の上にいるなら
      if self.rect.bottom < 768:
        # 鳥のy座標を速度の分だけ増加
        self.rect.y += int(self.vel)

    # ゲームオーバーになっていないなら
    if game_over == False:
      # マウスをクリックしたら
      if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
        # クリックフラグを更新
        self.clicked = True
        # 速度は減少。つまり上に飛ぶ。ゲーム内のY座標は上が負。
        self.vel = -10

      # マウスを左クリックを離したら
      if pygame.mouse.get_pressed()[0] == 0:
        # クリックフラグを更新
        self.clicked = False

      # カウンター増加
      self.counter += 1
      # 羽ばたきをクールダウン
      flap_cooldown = 5

      # カウンターがクールダウン変数より大きくなったら
      if self.counter > flap_cooldown:
        # カウンターを0に戻す
        self.counter = 0
        # 画像indexを増加
        self.index += 1
        # 画像indexが画像の枚数よりも大きくなったら
        if self.index >= len(self.images):
          # 画像indexを0に戻す
          self.index = 0

        # インデックスを用いて画像を指定
        self.image = self.images[self.index]

        # 画像を傾ける
        self.image = pygame.transform.rotate(self.images[self.index], self.vel * -2)
    else:
        # ゲームオーバーになったら、鳥の向きは-90度回転。真下に落ちているように見える
        self.image = pygame.transform.rotate(self.images[self.index], -90)

class Pipe(pygame.sprite.Sprite):
  """
  土管クラス
  """
  def __init__(self, x, y, position):
    """
    初期化関数、インスタンス生成時に呼ばれる関数
    """
    pygame.sprite.Sprite.__init__(self)
    # 土管画像をロード
    self.image = pygame.image.load("../img/pipe.png")
    # 土管画像を囲む四角形を取得
    self.rect = self.image.get_rect()

    # position=1のときは上の土管
    if position == 1:
      # 土管の画像を上下反転させる
      self.image = pygame.transform.flip(self.image, False, True)
      # 隙間を考慮して配置
      self.rect.bottomleft = [x, y - int(pipe_gap / 2)]

    # position=-1のときは下の土管
    if position == -1:
      # 隙間を考慮して配置
      self.rect.topleft = [x, y + int(pipe_gap / 2)]

  def update(self):
    """
    更新関数 フレーム毎に実行
    """
    # スクロールスピードの分だけX座標を動かす。距離=速度*時間であるが、時間は単位時間としていいので1とできる。だからX座標に速度を足すことができる。
    self.rect.x -= scroll_speed

    # 土管の右端がゲーム画面左端に消えたらkillして削除。
    if self.rect.right < 0:
      self.kill()


class Button():
  def __init__(self, x, y, image):
    """
    初期化関数、インスタンス生成時に呼ばれる関数
    """
    # 画像を入れる変数
    self.image = image
    # ボタン画像を囲む四角形
    self.rect = self.image.get_rect()
    # ボタンの左上の座標を指定
    self.rect.topleft = (x, y)

  def draw(self):
    """
    描画関数
    """
    # アクションフラグ
    action = False

    # マウスの座標
    pos = pygame.mouse.get_pos()

    # ボタンのクリック判定。マウスポインタの座標とボタン画像を囲む四角形との衝突判定。collide=衝突
    if self.rect.collidepoint(pos):
      # マウスをクリックした状態なら
      if pygame.mouse.get_pressed()[0] == 1:
        # アクションフラグを更新
        action = True

    # 指定の場所にボタン画像を描画
    screen.blit(self.image, (self.rect.x, self.rect.y))

    # アクションフラグを返す
    return action

# 鳥のスプライト画像のグループ
bird_group = pygame.sprite.Group()
# 土管のスプライト画像のグループ
pipe_group = pygame.sprite.Group()

# 鳥のインスタンス
flappy = Bird(100, int(screen_height / 2))

# 鳥グループに鳥インスタンスを追加
bird_group.add(flappy)

# ボタンのインスタンス
button = Button(screen_width // 2 - 50, screen_height // 2 - 100, buttom_img)


# ゲームの実行フラグ
run = True

# ゲームが実行中
while run:

  # 指定したfpsで描画
  clock.tick(fps)

  # 背景を描画
  screen.blit(bg, (0, 0))

  # 鳥をゲーム画面に描画
  bird_group.draw(screen)
  # 鳥を更新
  bird_group.update()

  # 土管をゲーム画面に描画
  pipe_group.draw(screen)

  # 地面の画像を描画
  screen.blit(ground_img, (ground_scroll, 768))

  # 土管の数が0以上なら
  if len(pipe_group) > 0:

    # 鳥の左端の座標が土管の左端より大きい、かつ、鳥の右端の座標が土管の右端の画像より小さい、かつ、通過フラグがFalse
    if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.left and bird_group.sprites()[0].rect.right < pipe_group.sprites()[0].rect.right and pass_pipe == False:
      # 通過フラグを更新
      pass_pipe = True

    # 通過フラグがTrueなら
    if pass_pipe == True:
      # 鳥の画像の左端の座標が土管の右端の座標よりも大きいなら
      if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.right:
        # スコアを加算
        score += 1
        
        # 通過フラグをFalseに戻す
        pass_pipe = False

  # スコアを描画
  draw_text(str(score), font, white, int(screen_width / 2), 20)

  # 鳥と土管の衝突判定、または、鳥の上部が画面外にある
  if pygame.sprite.groupcollide(bird_group, pipe_group, False, False) or flappy.rect.top < 0:
    # ゲームオーバーフラグを更新
    game_over = True

  # 鳥の下端が地面より下
  if flappy.rect.bottom > 768:
    # ゲームオーバーフラグを更新
    game_over = True
    # 飛行終了
    flying = False

  # ゲームオーバーでない、かつ、飛行中
  if game_over == False and flying == True:

    # 時間を取得
    time_now = pygame.time.get_ticks()

    # 最後に出現した土管から一定の時間が立っていたら
    if time_now - last_pipe > pipe_frequency:
      # -100~100のランダムな整数値
      pipe_height = random.randint(-100, 100)
      # 下の土管を配置
      btm_pipe = Pipe(screen_width, int(screen_height / 2) + pipe_height, -1)

      # 上の土管を配置
      top_pipe = Pipe(screen_width, int(screen_height / 2) + pipe_height, 1)

      # 土管グループに下の土管を追加
      pipe_group.add(btm_pipe)
      # 土管グループに上の土管を追加
      pipe_group.add(top_pipe)

      # 最後に出現した土管の時間を更新
      last_pipe = time_now

    # 地面のスクロール変数を更新
    ground_scroll -= scroll_speed

    # 地面のスクロール変数の絶対値が35以上になったら
    if abs(ground_scroll) > 35:
      地面のスクロール変数を0に戻す
      ground_scroll = 0

    # 土管を更新
    pipe_group.update()

  # ゲームオーバーなら
  if game_over == True:
    # リスタートボタンを押したなら
    if button.draw() == True:
      # ゲームオーバーフラグを戻す
      game_over = False
      # ゲームをリセット
      score = reset_game()

  for event in pygame.event.get():
    # ゲーム終了のためのキー操作
    if event.type == pygame.QUIT:
      run = False

    # マウスをクリックすると飛行する
    if event.type == pygame.MOUSEBUTTONDOWN and flying == False and game_over == False:
      flying = True

  # ゲーム画面を更新
  pygame.display.update()

# ゲームを終了
pygame.quit()