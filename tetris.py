import os
import sys
import random
import time
import pygame
from pygame.locals import *
from drew import *


class Box(object):
    def __init__( self, pygame, canvas, name, rect, color):
        self.pygame = pygame
        self.canvas = canvas
        self.name = name
        self.rect = rect
        self.color =color

        self.visivle = True
        

    def update(self):
        if(self.visivle):
            self.pygame.draw.rect( self.canvas, self.color, self.rect)





BRICK_DROP_RAPIDLY = 0.01
BRICK_DOWN_SPEED_MAX = 0.5


CANVAS_WIDTH = 800
CANVAS_HEIGHT = 600


COLOR_BLOCK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_RED = (255, 0, 0)
COLOR_GRAY = (107, 130, 114)
COLOR_GRAY_BLOCK = (20, 31, 23)
COLOR_GRAY_GREEN = (0, 255, 0)

# 定義方塊.
BRICK_DICT = {
    "10": (4, 8, 9, 13), "11": (9, 10, 12, 13),
    "20": (5, 8, 9, 12), "21": (8, 9, 13, 14),
    "30": (8, 12, 13, 14), "31": (4, 5, 8, 12), "32": (8, 9, 10, 14), "33": (5, 9, 12, 13),
    "40": (10, 12, 13, 14), "41": (4, 8, 12, 13), "42": (8, 9, 10, 12), "43": (4, 5, 9, 13),
    "50": (9, 12, 13, 14), "51": (4, 8, 9, 12), "52": (8, 9, 10, 13), "53": (5, 8, 9, 13),
    "60": (8, 9, 12, 13),
    "70": (12, 13, 14, 15), "71": (1, 5, 9, 13)
}




bricks_array = [[0]*20 for _ in range(10)]
bricks = [[0] * 4 for _ in range(4)]
bricks_next = [[0] * 4 for _ in range(4)]
bricks_next_object = [[0] * 4 for _ in range(4)] 
bricks_list = [[0] * 20 for _ in range(10)]
# 方塊在容器的位置.
#(-2~6)(為6的時候不能旋轉方塊).
container_x = 3
# (-3~16)(-3表示從上邊界外開始往下掉).
container_y =-4


debug_message = False
game_over = False


brick_down_speed = BRICK_DOWN_SPEED_MAX

# 方塊編號(1~7).
brick_id = 1
# 方塊狀態(0~3).
brick_state = 0

brick_next_id = 1

# 最大連線數.
lines_number_max = 0
# 本場連線數.
lines_number = 0

# 遊戲狀態.
# 0:遊戲進行中;1:清除方塊.
game_mode = 0


def show_font(text, x, y, color):
        text = font.render(text, True, color)
        canvas.blit(text, (x, y))

#取得方塊索引.
def get_brick_index(brick_id, state):
        global brick_dict
        brick_key = str(brick_id) + str(state)
        return BRICK_DICT[brick_key]

# 轉換方塊到方塊陣列.
def transform_to_bricks( brick_id, state):
        global bricks
        for x in range(4):
            for y in range(4):
                bricks[x][y] = 0
        p_brick = get_brick_index(brick_id, state)
        for i in range(4):
            bx = int(p_brick[i] % 4)
            by = int(p_brick[i] /4)
            bricks[bx][by] = brick_id


# 判斷是否可以複製到容器內.
def if_copy_to_bricks_array():
        global bricks, bricks_array
        global container_x, container_y

        posX = 0
        posY = 0
        for x in range(4):
            for y in range(4):
                if bricks[x][y] != 0:
                    posX = container_x + x
                    posY = container_y + y
                    if (posX >=0 and posY>=0):

                        try:
                            if bricks_array[posX][posY] != 0:
                                return False
                        except IndexError:
                            return False
        return True

# 複製方塊到容器內.
def copy_to_bricks_array():
        global bricks, bricks_array
        global container_x, container_y 
        posX=0
        posY=0
        for x in range(4):
            for y in range(4):
                if bricks[x][y] != 0:
                    posX = (container_x + x)
                    posY = (container_y + y)
                    if (posX >= 0 and posY >= 0):
                        bricks_array[posX][posY] = bricks[x][y]
                
     
# 初始化遊戲
def reset_game():
        global BRICK_DOWN_SPEED_MAX
        global bricks_array, bricks, lines_number, lines_number_max
        for x in range(10):
            for y in range(20):
                bricks_array[x][y] = 0
        for x in range(4):
            for y in range(4):
                bricks[x][y] = 0
        brick_down_speed = BRICK_DOWN_SPEED_MAX
        if(lines_number > lines_number_max):
          lines_number_max = lines_number
        lines_number = 0

# 判斷與設定要清除的方塊.
def if_clear_brick():
        point_num = 0
        line_num = 0
        for y in range(20):
            if all(bricks_array[x][y] > 0 for x in range(10)):
                point_num+=1
            if (point_num == 10):              
                for i in range(10):
                    line_num+=1
                    bricks_array[i][y] =9
            point_num = 0  
        return line_num

# 更新下一個方塊.
def update_next_bricks(brick_id):
        global bricks_next
        for y in range(4):
            for x in range(4):
                bricks_next[x][y] = 0
        p_brick = get_brick_index(brick_id, 0)
        for i in range(4):
            bx = int(p_brick[i] % 4)
            by = int(p_brick[i] /4)
            bricks_next[bx][by] = brick_id
        background_bricks_next.update()
        pos_y = 52
        for y in range(4):
            pos_x = 592
            for x in range(4):
                if bricks_next[x][y] != 0:
                    bricks_next_object[x][y].rect[0] = pos_x
                    bricks_next_object[x][y].rect[1] = pos_y
                    bricks_next_object[x][y].update()
                pos_x += 28
            pos_y += 28

# 產生新方塊.
def brickNew():
    global game_over, container_x, container_y, brick_id, brick_next_id, brick_state
    global lines_number, game_mode

    game_over = False
    if (container_y < 0):
        game_over = True

    container_y -=1
    copy_to_bricks_array()  
    

# 連線數累加.
    lines = if_clear_brick() / 10;        
    if (lines > 0):
        lines_number +=lines
        game_mode = 1
    container_x = 3
    container_y =-4
    brick_id = brick_next_id
    brick_next_id = random.randint( 1, 7)
    brick_state = 0
    if (game_over):
        reset_game()
    

# 清除方塊.
def clearBrick():
    global bricks_array
# 判斷要清除的方塊.
    temp = 0    
    for x in range(10):
        for i in range(19):
            for y in range(20):
                if (bricks_array[x][y] == 9):
                    if (y > 0):
                        temp = bricks_array[x][y - 1]
                        bricks_array[x][y - 1] = bricks_array[x][y]
                        bricks_array[x][y] = temp
                        y = y - 1
            bricks_array[x][0] = 0

pygame.init()
pygame.display.set_caption("Tetris Game")
canvas = pygame.display.set_mode((CANVAS_WIDTH ,CANVAS_HEIGHT))


clock = pygame.time.Clock()
font = pygame.font.SysFont("simsunnsimsun", 20)


# 將繪圖方塊放入陣列.
for y in range(20):
    for x in range(10):
        bricks_list[x][y] = Box(pygame, canvas, "brick_x_" + str(x) + "_y_" + str(y), [ 0, 0, 26, 26], COLOR_GRAY_BLOCK)

for y in range(4):
    for x in range(4):
        bricks_next_object[x][y] = Box(pygame, canvas, "brick_next_x_" + str(x) + "_y_" + str(y), [ 0, 0, 26, 26], COLOR_GRAY_BLOCK)


background = Box(pygame, canvas, "background", [ 278, 18, 282, 562], COLOR_GRAY)
background_bricks_next = Box(pygame, canvas, "background_bricks_next", [ 590, 50, 114, 114], COLOR_GRAY)


brick_next_id = random.randint( 1, 7)
brickNew()


running = True
time_temp = time.time()
time_now = 0
while running:
    time_now = time_now + (time.time() - time_temp)
    time_temp = time.time()
# 判斷輸入.
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False        

# 判斷按下按鈕
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_d:
                debug_message = not debug_message                
            # 變換方塊-上.
            elif event.key == pygame.K_UP and game_mode == 0:
                # 在右邊界不能旋轉.
                if (container_x == 8):
                    break
                # 判斷磚塊N1、N2、I.
                if (brick_id == 1 or brick_id == 2 or brick_id == 7):
                    # 長條方塊旋轉處理.
                    if (brick_id == 7):
                        if (container_x < 0 or container_x == 7):
                            break
                    # 旋轉方塊.
                    brick_state = brick_state + 1
                    if (brick_state > 1):
                        brick_state = 0                    
                    # 轉換方塊到方塊陣列.
                    transform_to_bricks(brick_id, brick_state)
                    # 碰到方塊.
                    if (not if_copy_to_bricks_array()):
                        brick_state = brick_state - 1
                        if (brick_state < 0):
                            brick_state = 1
                # 判斷方塊L1、L2、T.                                
                elif (brick_id == 3 or brick_id == 4 or brick_id == 5):
                    brick_state = brick_state + 1
                    if (brick_state > 3):
                        brick_state = 0                 
                    transform_to_bricks(brick_id, brick_state)
                    if (not if_copy_to_bricks_array()):
                        brick_state = brick_state - 1
                        if (brick_state < 0):
                            brick_state = 3
            # 快速下降-下.
            elif event.key == pygame.K_DOWN and game_mode == 0:
                # 方塊快速下降.
                brick_down_speed = BRICK_DROP_RAPIDLY
            # 移動方塊-左.
            elif event.key == pygame.K_LEFT and game_mode == 0:
                container_x = container_x - 1
                if (container_x < 0):
                    if (container_x == -1):
                        if (bricks[0][0] != 0 or bricks[0][1] != 0 or bricks[0][2] != 0 or bricks[0][3] != 0):
                            container_x = container_x + 1
                    elif (container_x == -2): 
                        if (bricks[1][0] != 0 or bricks[1][1] != 0 or bricks[1][2] != 0 or bricks[1][3] != 0):
                            container_x = container_x + 1
                    else:
                        container_x = container_x + 1
                if (not if_copy_to_bricks_array()):
                    container_x = container_x + 1
            # 移動方塊-右.
            elif event.key == pygame.K_RIGHT and game_mode == 0:
                container_x = container_x + 1
                if (container_x > 6):
                    if (container_x == 7):
                        if (bricks[3][0] != 0 or bricks[3][1] != 0 or bricks[3][2] != 0 or bricks[3][3] != 0):
                            container_x = container_x - 1;                        
                    elif (container_x == 8):
                        if (bricks[2][0] != 0 or bricks[2][1] != 0 or bricks[2][2] != 0 or bricks[2][3] != 0):
                            container_x = container_x - 1                        
                    else:
                        container_x = container_x - 1
                if (not if_copy_to_bricks_array()):
                    container_x = container_x - 1                    
  
        # 判斷放開按鈕
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_DOWN:
                # 恢復正常下降速度.
                brick_down_speed = BRICK_DOWN_SPEED_MAX
            
    # 清除畫面.
    canvas.fill(COLOR_BLOCK)

    if (game_mode == 0):
        # 處理方塊下降.
        if(time_now >= brick_down_speed):
            container_y = container_y + 1; 
            if (not if_copy_to_bricks_array()):
                brickNew()            
            transform_to_bricks( brick_id, brick_state)
            time_now = 0
    # 清除方塊.
    elif (game_mode == 1):
        clearBrick()
        game_mode = 0
        transform_to_bricks(brick_id, brick_state)


    update_next_bricks(brick_next_id)
    # 更新繪圖.
    pos_y = 20
    # 更新背景區塊.
    background.update()
    for y in range(20):
        pos_x = 280
        for x in range(10):
            if(bricks_array[x][y] != 0):
                bricks_list[x][y].rect[0] = pos_x
                bricks_list[x][y].rect[1] = pos_y
                bricks_list[x][y].update()
            pos_x = pos_x + 28        
        pos_y = pos_y + 28    
    # 更新方塊
    for y in range(4):
        for x in range(4):            
            if (bricks[x][y] != 0):
                posX = container_x + x
                posY = container_y + y
                if (posX >= 0 and posY >= 0):
                    bricks_list[posX][posY].rect[0] = (posX * 28) + 280
                    bricks_list[posX][posY].rect[1] = (posY * 28) + 20
                    bricks_list[posX][posY].update()    
    # 除錯訊息.
    if(debug_message):
        # 更新容器.
        str_x = ""
        pos_x = 15
        pos_y = 20
        for y in range(20):
            str_x = ""
            for x in range(10):
                str_x = str_x + str(bricks_array[x][y]) + " "
            showFont( str_x, pos_x, pos_y, COLOR_RED)
            pos_y = pos_y + 28
            
        # 更新方塊
        posX = 0
        posY = 0    
        for y in range(4):
            str_x = ""
            for x in range(4):            
                if (bricks[x][y] != 0):
                    posX = container_x + x
                    posY = container_y + y
                    if (posX >= 0 and posY >= 0):
                        str_x = str_x + str(bricks[x][y]) + " "
                else:
                    str_x = str_x + "  "
            pos_x = 15 + (container_x * 26)
            pos_y = 20 + (posY * 28)
            showFont( str_x, pos_x, pos_y, COLOR_WHITE)

    # 顯示訊息.
    show_font(f"Lines: {lines_number}", 600, 200, COLOR_RED)
    show_font(f"Max lines: {lines_number_max}", 600, 240, COLOR_RED)
    # 顯示FPS.
    if(debug_message):    
        showFont( u"FPS:" + str(clock.get_fps()), 6, 0, COLOR_GRAY_GREEN)    

   .
    pygame.display.update()
    clock.tick(50)

pygame.quit()
quit()
