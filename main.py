import pygame
from pygame import mixer
import random
import time
import enum

pygame.init()

# Global state variables
grid = None
running = None
gameover = None
won = None
score = None
best_score = None
record = None

# Pygame resources
# images
icon = pygame.image.load('assets/icon.png'); 

# fonts
font = pygame.font.Font('assets/BebasNeue-Regular.ttf', 96) # 75pt = 100px, 96pt = 128px
font2 = pygame.font.Font('assets/BebasNeue-Regular.ttf', 36) # 75pt = 100px, 96pt = 128px

# audio
mixer.music.load('assets/background.mp3')
mixer.music.play()
slide_sound = mixer.Sound('assets/blop.mp3')
record_sound = mixer.Sound('assets/unlock.mp3')

# animation
animation_stack = []

# Enums
class Dir(enum.IntEnum):
    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3

def start():
    ''' Initializes the game, sets default variable values.
    Called before game ran.
    '''
    global grid, running, gameover, won, score, best_score, record

    grid = [
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0]
    ]
    running = True
    gameover = False
    won = False
    score = 0
    best_score = 0
    record = False

    with open('./best_score.txt') as best_score_file:
        best_score = int(best_score_file.read())

    # Generate 2 random numbers + update the grid
    update()
    update()

def gameover():
    ''' Will be called when player lose the game.
    '''
    # Update best score in the file
    with open('./best_score.txt') as best_score_file:
        best_score = int(best_score_file.read())
    if score > best_score:
        with open('./best_score.txt', 'w') as best_score_file:
            best_score_file.write(str(score))

    start()

def whether_gameover():
    ''' Checks whether grid is full and you can't merge any tiles
    '''
    global grid

    # All grid slide directions
    for rot in 0, 1, 2, 3:
        for row in 1, 2, 3:
            for col in 0, 1, 2, 3:
                cur = translate_row_col(rot, row, col)
                above = translate_row_col(rot, row - 1, col)

                if grid[above[0]][above[1]] == 0:
                    return False
                elif grid[above[0]][above[1]] == grid[cur[0]][cur[1]]:
                    return False
    return True

def update():
    ''' Updates the grid every tile event occur.
    '''
    global grid, won, gameover

    empty_tiles = []
    for row in 0, 1, 2, 3:
        for col in 0, 1, 2, 3:
            if grid[row][col] == 0:
                empty_tiles.append((row, col))
            elif grid[row][col] == 2048:
                won = True
                return

    if whether_gameover():
        gameover = True
        return

    # Generate random number at random tile
    tile = random.choice(empty_tiles)
    grid[tile[0]][tile[1]] = random.randint(1, 2) * 2

def translate_row_col(r, row, col):
    ''' Translates index (row, col) to the rotated grid.
    '''
    # 0º rotation
    if r == 0:
        row2, col2 = row, col
    # 90º rotation
    elif r == 1:
        row2, col2 = col, 3 - row
    # 180º rotation
    elif r == 2:
        row2, col2 = 3 - row, 3 - col
    # 270º/-90º rotation
    elif r == 3:
        row2, col2 = 3 - col, row
    return row2, col2

def slide_tiles(d):
    ''' Slide and merge tiles in direction d.
    '''
    global grid, score

    for i in 1, 2, 3:
        for j in 0, 1, 2, 3:
            k = i
            # Merge tiles 
            while k != 0:
                # Translate to rotated grid
                cur = translate_row_col(d, k, j)
                above = translate_row_col(d, k-1, j)

                # Up is empty 
                if grid[above[0]][above[1]] == 0:
                    grid[above[0]][above[1]] += grid[cur[0]][cur[1]]
                    grid[cur[0]][cur[1]] = 0
                # Up is the same 
                elif grid[above[0]][above[1]] == grid[cur[0]][cur[1]]:
                    grid[above[0]][above[1]] += grid[cur[0]][cur[1]]
                    grid[cur[0]][cur[1]] = 0
                    # Increase score 
                    score += grid[above[0]][above[1]]
                # Up is other number (wall) 
                else:
                    pass

                k -= 1

# Displaying/ rendering part
size = 128*4 + 16*5, 128*4 + 16*5 + 64 + 16 # 128px - tile, 16px - spacing, 64px - score
screen = pygame.display.set_mode(size)
pygame.display.set_icon(icon)
pygame.display.set_caption('2048 in pygame!')

# Grid color
# Tile colors (12):
# 0, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048
# color value: str '0xrrggbb' or int 0xrrggbbaa
# with aa = 00, color not working for some reason

bg_color          = pygame.Color(0x8B, 0x5E, 0x34)
score_color         = pygame.Color('0xD4A276')
score_border_color  = pygame.Color('0x6F451800')
tile_colors = {}
tile_colors[0]      = pygame.Color('0xD4A276')
tile_colors[2]      = pygame.Color('0xF3D5B5')
tile_colors[4]      = pygame.Color('0xFFEDD8')
tile_colors[8]      = pygame.Color('0xFFEEC2')
tile_colors[16]     = pygame.Color('0xFFDD84')
tile_colors[32]     = pygame.Color('0xFFBA08')
tile_colors[64]     = pygame.Color('0xFAA307')
tile_colors[128]    = pygame.Color('0xF48C06')
tile_colors[256]    = pygame.Color('0xE85D04')
tile_colors[512]    = pygame.Color('0xDC2F02')
tile_colors[1024]   = pygame.Color('0xD00000')
tile_colors[2048]   = pygame.Color('0xBD0000')

def render():
    ''' Renders grid of tiles and score on the screen surface.
    '''
    global grid, score

    screen.fill(bg_color)

    # Render tiles
    for row in 0, 1, 2, 3:
        for col in 0, 1, 2, 3:
            # Tile
            tile_x = col*128 + (col+1)*16
            tile_y = row*128 + (row+1)*16 + 80
            tile = pygame.Rect(tile_x, tile_y, 128, 128)
            tile_color = tile_colors[grid[row][col]]
            tile_text_fg = (255, 255, 255) if grid[row][col]>16 else (0,0,0)
            tile_text_bg = tile_colors[grid[row][col]]
            tile_text = font.render(str(grid[row][col]), True, tile_text_fg)

            # resize text to fit into tile
            if grid[row][col] > 512:
                rel = 128 / text.get_width()
                text = pygame.transform.scale(text, (128, int(text.get_height() * rel)))

            tile_text_x = tile_x + 128//2 - tile_text.get_width()//2
            tile_text_y = tile_y + 128//2 - tile_text.get_height()//2

            # Tile
            pygame.draw.rect(screen, tile_color, tile, width=0, border_radius=7)
            if grid[row][col] != 0:
                screen.blit(tile_text, (tile_text_x, tile_text_y))

    # Score
    score_rect = pygame.Rect(16, 16, 128*2 + 16, 64)
    pygame.draw.rect(screen, score_color, score_rect, 0, 7)
    pygame.draw.rect(screen, score_border_color, score_rect, 5, 7)
    # text
    score_text = font2.render(f'Score: {score:8}', True, (255, 255, 255))
    score_text_x = 16 + (128*2+16)//2 - score_text.get_width()//2
    score_text_y = 16 + (64)//2 - score_text.get_height()//2
    screen.blit(score_text, (score_text_x, score_text_y))

    # Best score
    best_score_rect = pygame.Rect(16 + 128*2+16 + 16, 16, 128*2 + 16, 64)
    pygame.draw.rect(screen, tile_colors[0], best_score_rect, 0, 7)
    pygame.draw.rect(screen, score_border_color, best_score_rect, 5, 7)
    # text
    best_score_text = font2.render(f'Best score: {best_score:8}', True, (255, 255, 255))
    best_score_text_x = 16 + 128*2+16 + 16 + (128*2+16)//2 - best_score_text.get_width()//2
    best_score_text_y = 16 + (64)//2 - best_score_text.get_height()//2
    screen.blit(best_score_text, (best_score_text_x, best_score_text_y))

def render_splash(text):
    splash_surface = pygame.Surface((screen.get_width(), screen.get_height()))
    splash_surface.fill((0, 0, 0)); splash_surface.set_alpha(100)
    screen.blit(splash_surface, (0, 0))

    splash_text = font.render(text, True, (255, 255, 255))
    splash_text_x = screen.get_width()//2 - splash_text.get_width()//2
    splash_text_y = screen.get_height()//2 - splash_text.get_height()//2 + 20
    screen.blit(splash_text, (splash_text_x, splash_text_y))


retry_rect = pygame.Rect(screen.get_width()//2 - 128//2, screen.get_height()//2 + 128 - 64, 128, 64)

def render_retry():
    global retry_rect
    pygame.draw.rect(screen, pygame.Color(tile_colors[0]), retry_rect, 0, 7)
    pygame.draw.rect(screen, pygame.Color(score_border_color), retry_rect, 5, 7)

    # Score text
    retry_text = font2.render(f'Retry', True, (255, 255, 255))
    retry_text_x = screen.get_width()//2 - 128//2 + 128//2 - retry_text.get_width()//2
    retry_text_y = screen.get_height()//2 + 128 - 64 + 64//2 - retry_text.get_height()//2
    screen.blit(retry_text, (retry_text_x, retry_text_y))


clk = pygame.time.Clock()
fps_limit = 60

start()
while running:
    clk.tick(fps_limit)

    # Input
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            # Prepare to the quit
            running = False
        elif e.type == pygame.MOUSEBUTTONDOWN:
            if retry_rect.collidepoint(e.pos):
                # Restart the game
                start()

        elif e.type == pygame.KEYDOWN:
            if e.key == pygame.K_ESCAPE:
                running = False
            elif e.key == pygame.K_q:
                running = False

            # Skip arrow keys input
            if gameover or won:
                break

            if e.key == pygame.K_UP:
                # print('up')
                slide_tiles(Dir.UP)
                update()
                slide_sound.play()
            elif e.key == pygame.K_DOWN:
                # print('down')
                slide_tiles(Dir.DOWN)
                update()
                slide_sound.play()
            elif e.key == pygame.K_RIGHT:
                # print('right')
                slide_tiles(Dir.RIGHT)
                update()
                slide_sound.play()
            elif e.key == pygame.K_LEFT:
                # print('left')
                slide_tiles(Dir.LEFT)
                update()
                slide_sound.play()
            elif e.key == pygame.K_SPACE:
                # play_animation() - event based animation
                # NOT IMPORTANT
                pass

        if score > best_score:
            if not record:
                record_sound.play()
                record = True
            best_score = score

    # Update: no clock-cycle update in event-based game

    # Render
    render()

    if gameover:
        render_splash('Game over!')
        render_retry()
    elif won:
        render_splash('You won!')
        render_retry()

    pygame.display.update()

pygame.quit()
