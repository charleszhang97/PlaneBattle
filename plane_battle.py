"""
飞机大战——Charles 2020/03
"""
import os
import sys  #  导入系统模块
import win32api
import time
import random   #  导入随机数
import re
import pygame   #  导入pygame模块
from pygame.locals import *    #  导入pygame本地策略

APP_ICON = "resources/game.ico"    #  设计游戏图标
IMG_BACKGROUND = random.choice(["resources/background_1.jpg","resources/background_2.jpg","resources/background_3.jpg","resources/background_4.jpg"])   # 设置窗体背景
#  设置敌机图片库常量元组
IMG_ENEMYS = ("resources/img-plane_1.png","resources/img-plane_2.png","resources/img-plane_3.png","resources/img-plane_4.png","resources/img-plane_5.png","resources/img-plane_6.png","resources/img-plane_7.png")
IMG_PLAYER = "resources/hero2.png"    #  设置玩家飞机图片
IMG_BULLET = "resources/bullet_14.png"    #  设置子弹图片
#  创建所有显示的图形父类Model
class Model:
    window = None   #  主窗体对象，用于模型访问使用
    #  构造方法
    def __init__(self, img_path, x, y):
        self.img = pygame.image.load(img_path).convert_alpha()  #  背景图片
        self.x = x  #  窗体中放置的x坐标
        self.y = y  #  窗体中放置的y坐标
    #  将模型加入窗体的方法抽取到父类
    def display(self):
        Model.window.blit(self.img, (self.x, self.y))  # 填充图片到窗体中
    @staticmethod   #  碰撞操作与模型对象无关，属于模型相关操作，定义为静态方法
    def is_hit(rect1, rect2):     #  定义双方是否碰撞的静态方法
        return pygame.Rect.colliderect(rect1, rect2)     #  返回两个矩形是否相交，即是否碰撞
# 背景类
class Background(Model):
    #  定义背景移动的方法
    def move(self):
        #  加入判断
        if self.y < Game.WINDOW_HEIGHT:   #  更新高度的引用  #  如果没有超出屏幕就正常移动
            self.y += 1  #  纵坐标自增1
        else:   #  如果超出屏幕，恢复图片位置为原始位置
            self.y = 0  #  纵坐标 = 0
    #  覆盖父类display方法，做辅助背景贴图
    def display(self):
        Model.window.blit(self.img, (self.x, self.y))            #  原始背景贴图，推荐使用super().display()
        Model.window.blit(self.img, (self.x, self.y - Game.WINDOW_HEIGHT))      #  更新高度的引用  #  辅助背景即将原始背景图片展示第二遍，坐标位置与第一遍展示上下拼接吻合
# 玩家类
class PlayerPlane(Model):
    #  覆盖init方法
    def __init__(self,img_path, x, y):
        super().__init__(img_path, x, y)    #  调用父类构造方法
        self.bullets = []   #  定义子弹列表为空，默认没有子弹
        self.score = 0
    #  覆盖display方法
    def display(self,enemys):   #  在显示飞机和子弹的同时，传入敌机列表，判断子弹是否与敌机相撞，添加enemys形参
        super().display()    #  调用父类方法
        remove_bullets = []     #  定义被删除的子弹列表
        for bullet in self.bullets:     #  循环子弹
            #  优化子弹存储队列，超出屏幕移出子弹
            if bullet.y < -73:     #  如果子弹位置超出屏幕
                remove_bullets.append(bullet)   #  将要删除的子弹加入列表
            else:   #  如果子弹位置未超出屏幕范围
                rect_bullet = Rect(bullet.x, bullet.y, 20, 73)    #  创建子弹矩形对象，传入x,y,width,height
                # rect_bullet = bullet.img.get_rect()  # 无效
                for enemy in enemys:    #  对未超出屏幕显示范围的子弹与所有敌机进行碰撞检测
                    if bullet.y <= enemy.y + 68:  # 优化碰撞检测，仅当垂直方向相遇，才做碰撞判断
                        rect_enemy = Rect(enemy.x, enemy.y, 100, 68)     #  创建敌机矩形对象，传入x,y,width,height
                        # rect_enemy = enemy.img.get_rect()  # 无效
                        #  调用碰撞检测方法，传入当前子弹对象，传入敌机对象，判断是否碰撞
                        if Model.is_hit(rect_bullet, rect_enemy):   #  如果碰撞
                            enemy.is_hited = True   #  击中敌机即设置当前敌机为被击中状态
                            enemy.bomb.is_show = True       #  设置爆破效果状态开启
                            enemy.bomb.x, enemy.bomb.y = enemy.x, enemy.y  #  设置爆破效果开启位置x坐标/y坐标
                            remove_bullets.append(bullet)   #  将产生碰撞的子弹加入删除列表
                            self.score += 1
                            break       #  当前子弹击中了一架敌机，终止对剩余敌机的碰撞检测，终止敌机循环
        for bullet in remove_bullets:   #  循环删除子弹列表
            self.bullets.remove(bullet)  #  从原始子弹列表中删除要删除的子弹

        rect_player = Rect(self.x, self.y+10, 120, 78-10*2)   #  创建玩家矩形对象
        for enemy in enemys:   #  循环敌机列表
            if self.y <= enemy.y + 68:  # 优化碰撞检测，仅当垂直方向两机相遇，才做碰撞判断（敌机高度68）
                #  调用碰撞检测方法，传入玩家对象，传入敌机对象，判断是否碰撞
                rect_enemy = Rect(enemy.x+10, enemy.y+8, 100-10*2, 68-8*2)    #  创建敌机矩形对象
                if Model.is_hit(rect_player, rect_enemy):   #  如果碰撞
                    # enemy.is_hited = True   #  设置当前敌机为被击中状态
                    pygame.mixer.music.load("resources/gameover.wav")  #  加载游戏背景音乐文件为游戏结束
                    pygame.mixer.music.play(loops=1)   #  播放背景音乐  loops=1 控制播放次数
                    return 2    #  设置当前操作返回2,表示游戏结束
        return 1    #  设置正常操作状态下返回1，表示游戏进行中
# 敌机类
class EnemyPlane(Model):
    #  覆盖init方法
    def __init__(self):
        # img = IMG_ENEMYS[random.randint(0,len(IMG_ENEMYS)-1)]   #  设置图片路径随机从元组中获取
        img = random.choice(IMG_ENEMYS)
        x = random.randint(0, Game.WINDOW_WIDTH - 100)  #  设置x坐标随机生成 横向位置 0 到 屏幕宽度 - 飞机宽度(100)
        y = random.randint(-Game.WINDOW_HEIGHT, -68)    #  设置y坐标随机生成 纵向位置 -屏幕高度 到 -飞机高度
        super().__init__(img, x, y)   #  调用父类构造方法
        self.is_hited = False   #  添加敌机被击中的状态
        self.bomb = Bomb()      #  为敌机添加绑定的爆破效果对象
    #   定义敌机移动的方法
    def move(self):
        #  控制敌机到达底部后，返回顶部
        if self.y < Game.WINDOW_HEIGHT and not self.is_hited : #  添加敌机被击中的状态判定     #  敌机未超出屏幕
            self.y += 2 #  控制敌机移动速度
        else:   #  敌机超出屏幕
            # self.img = pygame.image.load(IMG_ENEMYS[random.randint(0, len(IMG_ENEMYS) - 1)]).convert_alpha()    #  修改敌机到达底部后返回的图片随机生成，同初始化策略
            self.img = pygame.image.load(random.choice(IMG_ENEMYS)).convert_alpha()
            self.x = random.randint(0, Game.WINDOW_WIDTH - 100) #  修改敌机到达底部后返回顶部的策略，x随机生成，同初始化策略
            self.y = random.randint(-Game.WINDOW_HEIGHT, -68)   #  修改敌机到达底部后返回顶部的策略，y随机生成，同初始化策略
            self.is_hited = False       #  重置敌机是否被击中状态为未被击中，False

    def display(self):  #  覆盖父类显示方法
        super().display()   #  调用父类显示方法，用于显示敌机自身
        if self.bomb.is_show:  #  如果开启爆破效果
            self.bomb.display() #  调用爆破对象的显示方法
# 子弹类
class Bullet(Model):
    #   定义子弹移动的方法
    def move(self):
        self.y -= 10    #  控制子弹移动速度
# 爆炸效果类
class Bomb(Model): #  创建爆炸效果类
    def __init__(self):     #  定义单独的初始化方法
        self.x = None       #  定义爆炸显示的横坐标x
        self.y = None       #  定义爆炸显示的纵坐标y
        self.imgs = [pygame.image.load("resources/bomb-"+str(i)+".png").convert_alpha() for i in range(1, 8)]     #  加载爆炸效果使用的所有图片列表
        self.is_show = False    #  定义是否开启爆破效果属性
        self.times = 0      #  定义爆破图片展示控制变量

    def display(self):      #  定义单独的贴图显示方法
        if self.is_show and self.times < len(self.imgs) * 10: #  延长播放次数，放大循环次数，拉长播放时间  #  控制爆破展示每次一轮，不能超过边界  #  如果开启爆破效果
            if self.times == 0:  # 首次调用时，播放爆炸音效（self.is_show不置为false，会一直调用display方法）
                sound = pygame.mixer.Sound("resources/bomb.wav")  # 添加混音音效文件
                sound.play()  # 播放爆破效果音
            Model.window.blit(self.imgs[self.times // 10], (self.x, self.y)) #  延长播放次数，放大循环次数，拉长播放时间  #  修改爆破图片展示每次递增  #  展示爆破图片第一张图片，用于测试效果
            self.times += 1     #  控制变量每次+1
        else:   #  控制爆破展示完毕后恢复状态
            self.times = 0          #  控制爆破展示完毕后恢复后下次展示图片从第一个开始
            self.is_show = False    #  控制爆破展示完毕后恢复后设置为不开始爆炸效果

        # 游戏类
class Game:
    WINDOW_WIDTH = 820  #  定义窗体宽度常量
    WINDOW_HEIGHT = 820 #  定义窗体高度常量
    FPS = 60  # 帧速率

    #  定义构造方法
    def __init__(self):
        self.game_status = 0  #  初始化游戏状态，0（默认）表示游戏未开始，1 表示游戏进行中，2 表示游戏结束
        self.exit_flag = False
        self.fullscreen = False
        self.difficulty_index = 0


    #  主程序，运行游戏入口
    def run(self):
        self.frame_init()   #  执行窗体初始化
        self.model_init()   #  执行元素初始化
        self.rank_init()

        pygame.time.set_timer(self.HERO_FIRE_EVENT, 150)  # 设置发射子弹事件定时器
        pygame.mixer.music.load("resources/bgm.wav")   #  加载背景音乐文件
        pygame.mixer.music.play(loops=100)                #  播放背景音乐

        font_score = pygame.font.Font("resources/DENGB.TTF", 32)  # 创建字体对象

        while not self.exit_flag:     #  构造反复执行的机制，刷新窗体，使窗体保持在屏幕上
            if self.game_status == 0:  #  判定游戏未开始状态操作
                self.background.display()

                font_over = pygame.font.Font("resources/DENGB.TTF", 40)  # TODO  设置大字体
                text_over = font_over.render("飞机大战", True, (255, 255, 0))  # TODO  设置文字
                self.window.blit(text_over, Rect(Game.WINDOW_WIDTH / 2 - 80, 200, 240, 40))  # TODO  设置显示位置

                font_over = pygame.font.Font("resources/DENGB.TTF", 20)  # TODO  设置小字体
                text_over = font_over.render("请选择难度", True, (255, 255, 255))
                self.window.blit(text_over, Rect(Game.WINDOW_WIDTH / 2 - 58, 330, 240, 40))

                font_over = pygame.font.Font("resources/DENGB.TTF", 24)  # TODO  设置中字体
                _x = Game.WINDOW_WIDTH / 2 - 45  # 偏移量
                all_select_rect = [Rect(0, 0, 0, 0), Rect(_x, 370, 75, 28), Rect(_x, 420, 75, 28), Rect(_x, 470, 75, 28)]
                text_over = font_over.render("1-简单", True, (0, 255, 0))
                self.window.blit(text_over, all_select_rect[1])
                text_over = font_over.render("2-普通", True, (0, 0, 255))
                self.window.blit(text_over, all_select_rect[2])
                text_over = font_over.render("3-困难", True, (255, 0, 0))
                self.window.blit(text_over, all_select_rect[3])
                pygame.draw.rect(self.window, (200, 200, 200), all_select_rect[self.difficulty_index], 3)

                pygame.time.delay(200)
            elif self.game_status == 1:  #  判定游戏进行中状态
                self.background.move()  # 背景操作放置在游戏状态判定外面，始终保持   # 调用背景移动操作，反复执行，构造背景向下的画面
                self.background.display()  # 背景操作放置在游戏状态判定外面，始终保持 # 反复刷新背景

                self.game_status = self.player.display(
                    self.enemys)  # 接收到游戏状态，备用   #  飞机加入时，传入敌机列表实参self.enemys #  玩家飞机贴图

                for bullet in self.player.bullets:  # 循环子弹
                    bullet.display()  # 每个子弹贴图
                    bullet.move()  # 调用子弹移动操作

                for enemy in self.enemys:  # 加入所有敌机
                    enemy.move()  # 每驾敌机移动
                    enemy.display()  # 每驾敌机贴图

                self.window.blit(font_score.render(str(self.player.score), True, (255, 0, 0)),
                                 Rect(10, 10, 300, 50))  # 显示分数到屏幕上
            elif self.game_status == 2:  #  判定游戏结束状态
                font_over = pygame.font.Font("resources/DENGB.TTF", 40)               #  创建字体对象
                text_obj = font_over.render("GAME OVER", True, (255, 0, 0))        #  创建文本对象
                self.window.blit(text_obj, Rect(Game.WINDOW_WIDTH / 2 - 116, 180, 240, 40))  # 添加文本对象到屏幕上

                font_over = pygame.font.Font("resources/DENGB.TTF", 24)  # TODO  设置小字体
                self.window.blit(font_over.render("------------排行榜------------", True, (255, 255, 0)),
                                 Rect(Game.WINDOW_WIDTH / 2 - 180, 250, 240, 40))
                # 制作透明背景
                surface_alpha = self.window.convert_alpha()
                surface_alpha.fill((255, 255, 255, 0))  # alpha=0,全透明
                width, height = 390, 316
                rect_rank_bg = pygame.Rect(215, 300, width, height)
                # pygame.draw.rect(self.window, (200, 200, 200), rect_rank_bg, 0)
                pygame.draw.rect(surface_alpha, (200, 200, 200, 10), rect_rank_bg, 0)
                self.window.blit(surface_alpha, (0, 0))
                # 循环显示出完整排行榜
                for score_index in range(len(self.rank_top10)):
                    text_over = font_over.render("%2d、%s" % (score_index+1, self.rank_top10[score_index]), True, (255, 255, 255))
                    self.window.blit(text_over, Rect(Game.WINDOW_WIDTH / 2 - 180, 310 + 30 * score_index, 240, 40))
                # time.sleep(0.2)
                pygame.time.delay(200)
            elif self.game_status == -1:  #  判定游戏暂停状态
                font_over = pygame.font.Font("resources/DENGB.TTF", 40)               #  创建字体对象
                text_obj = font_over.render("PAUSE！", True, (0, 0, 255))        #  创建文本对象
                self.window.blit(text_obj, Rect(Game.WINDOW_WIDTH / 2 - 71, 300, 240, 40))  # 添加文本对象到屏幕上
                # time.sleep(0.5)
                pygame.time.delay(500)

            pygame.display.update()  #  界面刷新操作，始终保持 # 刷新窗体
            # time.sleep(0.001)  # 减少CPU负担，1毫秒
            self.clock.tick(Game.FPS)
            self.event_handler()  #  事件相关操作，始终保持 # 反复监控是否存在事件执行
        pygame.quit()
        pygame.mixer.quit()
        print("pygame exit")
        sys.exit()  # 系统退出


    #  初始化窗体
    def frame_init(self):
        current_w = win32api.GetSystemMetrics(0)  # 获得屏幕分辨率X轴
        current_h = win32api.GetSystemMetrics(1)  # 获得屏幕分辨率Y轴
        # print(current_w, current_h)
        pos_x, pos_y = int((current_w - Game.WINDOW_WIDTH) / 2), int((current_h - Game.WINDOW_HEIGHT) / 2)
        os.environ["SDL_VIDEO_WINDOW_POS"] = "%d, %d" % (pos_x, pos_y)

        pygame.init()   #  初始化pygame读取系统操作
        pygame.mixer.init() #  初始化背景音乐模块
        self.window = pygame.display.set_mode((Game.WINDOW_WIDTH, Game.WINDOW_HEIGHT), 0, 32)    #  更新宽度和高度的引用  #  初始化窗体
        Model.window = self.window  #  将窗体对象传入模型类中
        img = pygame.image.load(APP_ICON).convert_alpha()  #  修改图片地址为常量引用 #  加载图标文件为图片对象
        pygame.display.set_icon(img)    #  设置窗体图标为图片
        pygame.display.set_caption("Plane Battle V1.0 - By Charles")    #  设置窗体的标题
        self.clock = pygame.time.Clock()  # for limiting FPS
        self.HERO_FIRE_EVENT = pygame.USEREVENT  # 定义英雄发射子弹事件ID


    #  初始化窗体中的元素
    def model_init(self):
        self.background = Background(IMG_BACKGROUND, 0, 0)     #  初始化背景对象，使用图片路径常量，放置在0,0位
        self.enemys = []    #  定义敌机列表，保存多驾敌机
        self.player = PlayerPlane(IMG_PLAYER, Game.WINDOW_WIDTH/2 - 120/2, 600)       #  初始化玩家飞机对象


    #  初始化排行榜信息
    def rank_init(self):
        # 以下获取、处理排行数据
        png_files = list()
        Game.list_dir(png_files)
        list_all_score = list()
        list_all_time = list()
        for png in png_files:
            # nums = re.findall(r"\d+", png)
            score_search = re.search(r"^(\d{4}-\d{2}-\d{2}) (\d{2}-\d{2}-\d{2}) score-(\d+)\.png$", png, re.I)
            if score_search and len(score_search.groups()) == 3:
                list_all_score.append(int(score_search.group(3)))
                list_all_time.append(score_search.group(1).replace("-", "/")+" "+score_search.group(2).replace("-", ":"))
        set_tmp_score = set(list_all_score)  # 去重
        list_tmp_score = list(set_tmp_score)
        list_tmp_score.sort(reverse=True)
        list_rank_score = list()
        png_files_bak = png_files.copy()
        for _score in list_tmp_score:
            idx = list_all_score.index(_score)
            list_rank_score.append(str(_score).ljust(10, " ") + list_all_time[idx])
            # png_files.pop(idx)  # 报错 索引超出范围
            png_files.remove(png_files_bak[idx])
            if len(list_rank_score) == 10:
                break
        # print(list_rank_score)
        # print(png_files)
        self.rank_top10 = list_rank_score
        Game.clear_dir(png_files)


    @classmethod
    def list_dir(cls, list_files):
        # abs_dir = __file__[0:__file__.rfind("/")+1] + "screenshots"
        abs_dir = os.path.join(os.path.dirname(__file__), "screenshots")
        if os.path.exists(abs_dir):
            for file in os.listdir(abs_dir):
                file_path = os.path.join(abs_dir, file)
                if os.path.isfile(file_path) and os.path.splitext(file)[1].lower() == ".png":
                    # list_files.append(os.path.basename(file_path))
                    list_files.append(file)


    @classmethod
    def clear_dir(cls, list_files_to_remove):
        abs_dir = os.path.join(os.path.dirname(__file__), "screenshots")
        if os.path.exists(abs_dir):
            for file in os.listdir(abs_dir):
                file_path = os.path.join(abs_dir, file)
                if os.path.isfile(file_path) and file in list_files_to_remove:
                    os.remove(file_path)
                    list_files_to_remove.remove(file)


    #  事件监听
    def event_handler(self):
        # event = pygame.event.wait()  # 阻塞直到发生事件
        for event in pygame.event.get():    #  获取所有的事件
            if event.type == QUIT:    #  判断是不是点击的关闭按钮
                self.exit_flag = True
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                self.exit_flag = True
            elif event.type == KEYDOWN and event.key == K_f:
                self.fullscreen = not self.fullscreen
                if self.fullscreen:
                    Model.window = self.window = pygame.display.set_mode((Game.WINDOW_WIDTH, Game.WINDOW_HEIGHT),
                                                          HWSURFACE | FULLSCREEN, 32)  # 硬件显示（显存加速），全屏显示
                else:
                    Model.window = self.window = pygame.display.set_mode((Game.WINDOW_WIDTH, Game.WINDOW_HEIGHT),
                                                                         0, 32)
            elif event.type == MOUSEMOTION: #  设置监听鼠标移动事件
                if self.game_status == 1:
                    pos = pygame.mouse.get_pos()        #  获取鼠标位置
                    self.player.x = pos[0] - 120/2     #  设置飞机中心位置在鼠标位置(x)  横坐标 - 飞机宽度1半
                    self.player.y = pos[1] - 78/2 + 5    #  设置飞机中心位置在鼠标位置(y)  纵坐标 - 飞机高度1半 +-微调数据
                    if self.fullscreen and self.player.x >= Game.WINDOW_WIDTH - 120/2:  # 修复全屏x超出画面
                        self.player.x = Game.WINDOW_WIDTH - 120/2 - 1
                elif self.game_status == 0:
                    pos = pygame.mouse.get_pos()  # 获取鼠标位置
                    # pygame.Rect.collidepoint()
                    _x = Game.WINDOW_WIDTH / 2 - 45
                    if Rect(_x, 370, 75, 28).collidepoint(*pos):
                        self.difficulty_index = 1
                    elif Rect(_x, 420, 75, 28).collidepoint(*pos):
                        self.difficulty_index = 2
                    elif Rect(_x, 470, 75, 28).collidepoint(*pos):
                        self.difficulty_index = 3
            elif event.type == self.HERO_FIRE_EVENT:
                self.player_fire_event_handler()
            elif self.game_status == 0:
                if event.type == KEYDOWN:
                    if event.key == 49 or event.key == K_1:
                        for _ in range(5):  # 循环产生5架敌机
                            self.enemys.append(EnemyPlane())  # 修改创建敌机操作 # 初始位置x为横向随机，纵向200
                        self.game_status = 1
                        self.difficulty_index = 1
                    elif event.key == 50 or event.key == K_2:
                        for _ in range(30):  # 循环产生30架敌机
                            self.enemys.append(EnemyPlane())  # 修改创建敌机操作 # 初始位置x为横向随机，纵向200
                        self.game_status = 1
                        self.difficulty_index = 2
                    elif event.key == 51 or event.key == K_3:
                        for _ in range(100):  # 循环产生100架敌机
                            self.enemys.append(EnemyPlane())  # 修改创建敌机操作 # 初始位置x为横向随机，纵向200
                        self.game_status = 1
                        self.difficulty_index = 3
                elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                    pos = pygame.mouse.get_pos()  # 获取鼠标位置
                    _x = Game.WINDOW_WIDTH / 2 - 45
                    if Rect(_x, 370, 75, 28).collidepoint(*pos) or Rect(_x, 420, 75, 28).collidepoint(*pos) or \
                            Rect(_x, 470, 75, 28).collidepoint(*pos):
                        self.game_status = 1
                        if self.difficulty_index == 1:
                            for _ in range(5):  # 循环产生5架敌机
                                self.enemys.append(EnemyPlane())  # 修改创建敌机操作 # 初始位置x为横向随机，纵向200
                        elif self.difficulty_index == 2:
                            for _ in range(30):  # 循环产生30架敌机
                                self.enemys.append(EnemyPlane())  # 修改创建敌机操作 # 初始位置x为横向随机，纵向200
                        elif self.difficulty_index == 3:
                            for _ in range(100):  # 循环产生100架敌机
                                self.enemys.append(EnemyPlane())  # 修改创建敌机操作 # 初始位置x为横向随机，纵向200
            elif self.game_status == 1:
                if event.type == KEYDOWN:
                    if event.key == K_LCTRL:  # 按下Ctrl键，开启暂停
                        self.game_status = -1
                        pygame.mixer.music.pause()
                    elif event.key == K_KP_PLUS:
                        self.enemys.append(EnemyPlane())
                    elif event.key == K_KP_MINUS:
                        if len(self.enemys) > 0:
                            enemy = self.enemys.pop()
                            enemy.bomb.is_show = True  # 设置爆破效果状态开启
                            enemy.bomb.x, enemy.bomb.y = enemy.x, enemy.y  # 设置爆破效果开启位置x，y坐标
                            while enemy.bomb.is_show:
                                enemy.bomb.display()
                                # enemy.bomb.times += 5  # 干预爆炸显示速度
                                pygame.display.update()
                                self.clock.tick(240)
                            del enemy.bomb, enemy
                    elif event.key == K_KP_MULTIPLY:
                        distance = Game.WINDOW_WIDTH / 10
                        for idx in range(10):
                            bullet = Bullet(IMG_BULLET, idx * distance + (distance / 2 - 20 / 2),
                                            Game.WINDOW_HEIGHT - 73)  # 创建子弹
                            self.player.bullets.append(bullet)  # 加入飞机子弹列表
                elif event.type == MOUSEBUTTONDOWN:
                    # if pygame.mouse.get_pressed()[2] == 1:  # 按下鼠标右键，开启暂停
                    if event.button == 3:  # 按下鼠标右键。event.pos 获取鼠标位置
                        self.game_status = -1
                        pygame.mixer.music.pause()
            elif self.game_status == 2:
                if (event.type == KEYDOWN and event.key == K_RETURN) or \
                        (event.type == MOUSEBUTTONDOWN and event.button == 3):  # 按下Enter键或鼠标右键，返回初始界面
                    self.game_reset()
                elif (event.type == KEYDOWN and event.key == K_s and pygame.key.get_mods() & pygame.KMOD_CTRL) or \
                        (event.type == MOUSEBUTTONDOWN and event.button == 2):  # 按下ctrl+s键或鼠标中键，保存分数截图
                    pygame.image.save(self.window,
                                      "screenshots/{0} score-{1}.png".format(time.strftime("%Y-%m-%d %H-%M-%S"), self.player.score))
                    self.rank_init()  # 刷新排行榜
                    self.background.display()  # 使用背景覆盖，遮蔽旧排行榜数据
            elif self.game_status == -1:
                if (event.type == KEYDOWN and event.key == K_LCTRL) or \
                        (event.type == MOUSEBUTTONDOWN and event.button == 3):  # 按下Ctrl键或鼠标右键，取消暂停
                    self.game_status = 1
                    pygame.mixer.music.unpause()
        if self.game_status == 0:
            pass
        elif self.game_status == 1:
            # 使用键盘模块可以持续获取键盘按键
            keys_pressed = pygame.key.get_pressed()
            # 判断元祖中对应的按键索引值
            flag_is_move = False
            if keys_pressed[K_LEFT] or keys_pressed[K_a]:
                self.player.x -= 10
                flag_is_move = True
            elif keys_pressed[K_RIGHT] or keys_pressed[K_d]:
                self.player.x += 10
                flag_is_move = True
            elif keys_pressed[K_UP] or keys_pressed[K_w]:
                self.player.y -= 10
                flag_is_move = True
            elif keys_pressed[K_DOWN] or keys_pressed[K_s]:
                self.player.y += 10
                flag_is_move = True
            # 修复x,y超出画面
            if flag_is_move:
                if self.player.x >= Game.WINDOW_WIDTH - 120 / 2:
                    self.player.x = Game.WINDOW_WIDTH - 120 / 2 - 1
                elif self.player.x < - 120 / 2:
                    self.player.x = - 120 / 2
                if self.player.y >= Game.WINDOW_HEIGHT - 78 / 2 + 5:
                    self.player.y = Game.WINDOW_HEIGHT - 78 / 2 - 1 + 5
                elif self.player.y < - 78 / 2 + 5:
                    self.player.y = - 78 / 2 + 5
        elif self.game_status == 2:
            pass


    # 处理玩家发射子弹事件（定时器调用）
    def player_fire_event_handler(self):
        if self.game_status == 1:
            key_pressed = pygame.key.get_pressed()  # 获取键盘所有按键状态
            mouse_pressed = pygame.mouse.get_pressed() #  获取鼠标按键压下状态，返回得到元组，其中保存鼠标左中右键按下状态（1,0,0）
            if mouse_pressed[0] == 1 or key_pressed[K_SPACE]:  #  判断左键或空格是否按下
                if len(self.player.bullets) < 1 * 5:
                    # pos = pygame.mouse.get_pos()  #  获取鼠标位置
                    # bullet = Bullet(IMG_BULLET, pos[0] - 20 / 2, pos[1] - 78 / 2 - 73)  #  创建子弹，横坐标为鼠标x坐标 - 子弹宽度1半，纵坐标为鼠标y坐标 - 飞机高度1版 - 子弹高度
                    _x, _y = self.player.x, self.player.y  #  获取玩家飞机位置
                    bullet = Bullet(IMG_BULLET, _x + 120 / 2 - 20 / 2, _y - 73)  #  创建子弹
                    self.player.bullets.append(bullet)  #  加入飞机子弹列表


    # 重置游戏，使用已有模型进行下一次游戏
    def game_reset(self):
        self.enemys.clear()
        self.player.bullets.clear()
        self.player.x, self.player.y = Game.WINDOW_WIDTH/2 - 120/2, 600
        self.game_status = 0
        self.difficulty_index = 0
        self.player.score = 0
        pygame.mixer.music.load("resources/bgm.wav")  # 加载背景音乐文件
        pygame.mixer.music.play(loops=100)  # 播放背景音乐

#  设置测试类入口操作
if __name__ == "__main__":
    Game().run()
