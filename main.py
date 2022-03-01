from random import randint

import pygame
import pygame_gui
import pytmx

WINDOW_SIZE = WINDOW_WIDTH, WINDOW_HEIGHT = 1600, 1024
TILE_SIZE = 16
MAPS_DIR = 'maps'
TIMER = pygame.USEREVENT + 1
coords = [(5, 13), (14, 13), (27, 13), (40, 13), (48, 13), (10, 32), (28, 32), (10, 49), (26, 49),
          (38, 49), (50, 49)]


class Postman:

    def __init__(self, filename, free_tiles, door_tiles):
        self.map = pytmx.load_pygame(f'{MAPS_DIR}/{filename}')
        self.height = self.map.height
        self.width = self.map.width
        self.tile_size = self.map.tilewidth
        self.free_tiles = free_tiles
        self.finish_tiles = door_tiles

    def render(self, screen):
        for y in range(self.height):
            for x in range(self.width):
                image = self.map.get_tile_image(x, y, 0)
                screen.blit(image, (x * self.tile_size, y * self.tile_size))

    def get_tile_id(self, position, layer):
        return self.map.tiledgidmap[self.map.get_tile_gid(*position, layer)]

    def is_free(self, position, layer):
        return self.get_tile_id(position, layer) in self.free_tiles

    def grab_mail(self, position, mails, backpack, backpack_capacity, layer=0):
        if self.get_tile_id((position[0], position[1] - 1), layer) == 37:
            for i in mails:
                if backpack_capacity > len(backpack):
                    backpack.append(i)
                    mails.remove(i)
                    return True
        return False

    def deliver_mail(self, position, backpack, layer=0):
        if self.get_tile_id((position[0], position[1] - 1), layer) in self.finish_tiles:
            for i in backpack:
                if position == coords[int(i) - 1]:
                    backpack.remove(i)
                    return True
        return False


class Guy:

    def __init__(self, pic, position):
        self.image = pygame.image.load(f'images/{pic}')
        self.x, self.y = position

    def get_position(self):
        return self.x, self.y

    def set_position(self, position):
        self.x, self.y = position

    def render(self, screen):
        delta = (self.image.get_width() - TILE_SIZE) // 2
        screen.blit(self.image, (self.x * TILE_SIZE - delta, self.y * TILE_SIZE - delta))


class Game:

    def __init__(self, level, guy):
        self.level = level
        self.guy = guy

    def render(self, screen):
        self.level.render(screen)
        self.guy.render(screen)

    def update_guy(self):
        next_x, next_y = self.guy.get_position()
        if pygame.key.get_pressed()[pygame.K_a]:
            next_x -= 1
        if pygame.key.get_pressed()[pygame.K_d]:
            next_x += 1
        if pygame.key.get_pressed()[pygame.K_w]:
            next_y -= 1
        if pygame.key.get_pressed()[pygame.K_s]:
            next_y += 1
        if self.level.is_free((next_x, next_y), 0):
            self.guy.set_position((next_x, next_y))


def show_message(screen, message):
    font = pygame.font.Font(None, 50)
    text = font.render(message, 1, (100, 100, 100))
    text_x = WINDOW_WIDTH // 2 - text.get_width() // 2
    text_y = WINDOW_HEIGHT // 2 - text.get_height() // 2
    text_w = text.get_width()
    text_h = text.get_height()
    pygame.draw.rect(screen, (0, 255, 0), (text_x - 10, text_y - 10, text_w + 20, text_h + 20))
    screen.blit(text, (text_x, text_y))


def stats_update(screen, name, stat, position):
    x, y = position
    font = pygame.font.Font(None, 30)
    text = font.render(f'{name}: {stat}', 1, (100, 100, 100))
    text_w = text.get_width()
    text_h = text.get_height()
    pygame.draw.rect(screen, (0, 255, 0), (x - 10, y - 10, text_w + 20, text_h + 20))
    screen.blit(text, (x, y))


def main():
    pygame.init()
    pygame.display.set_caption('Postman')
    pygame.display.set_icon(pygame.image.load('images/postman.png'))
    screen = pygame.display.set_mode(WINDOW_SIZE)

    manager = pygame_gui.UIManager((WINDOW_WIDTH, WINDOW_HEIGHT))
    shop_manager = pygame_gui.UIManager((WINDOW_WIDTH, WINDOW_HEIGHT))

    lvl1 = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((250, 250), (300, 100)),
        text='Уровень 1',
        manager=manager
    )
    lvl2 = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((250, 400), (300, 100)),
        text='Уровень 2',
        manager=manager
    )
    lvl3 = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((250, 550), (300, 100)),
        text='Уровень 3',
        manager=manager
    )
    lvl4 = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((250, 700), (300, 100)),
        text='Уровень 4',
        manager=manager
    )
    lvl5 = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((250, 850), (300, 100)),
        text='Уровень 5',
        manager=manager
    )

    shop_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((850, 500), (400, 200)),
        text='Магазин',
        manager=manager
    )

    buy_slots = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((350, 300), (400, 200)),
        text='Купить слот в рюкзак | Стоимость: 50 монет',
        manager=shop_manager
    )
    buy_speed = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((350, 700), (400, 200)),
        text='Увеличить скорость | Стоимость: 100 монет',
        manager=shop_manager
    )

    exit_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((1200, 100), (150, 50)),
        text='Выход в меню',
        manager=shop_manager
    )

    for i in [exit_button, buy_slots, buy_speed]:
        i.hide()
        i.disable()

    level = Postman('map.tmx', [28, 261, 291, ], [38, 39, 95, 96, 121, 122, 151])
    guy = Guy('postman.png', (42, 32))
    game = Game(level, guy)
    clock = pygame.time.Clock()
    pygame.mixer.music.load('music/8bit_nastolgia.mp3')

    bg = pygame.image.load('images/background.png')

    playing = False
    running = True
    score = 0
    difficulty = 1
    time = 60
    backpack_capacity = 1
    speed = 5

    while running:
        time_delta = clock.tick(speed) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame_gui.UI_BUTTON_START_PRESS:
                if event.ui_element == buy_slots:
                    if backpack_capacity < 3 and score >= 100:
                        backpack_capacity += 1
                        score -= 100
                if event.ui_element == buy_speed:
                    if speed < 15 and score >= 200:
                        speed += 5
                        score -= 200

                if event.ui_element in [lvl1, lvl2, lvl3, lvl4, lvl5]:
                    playing = True
                    if event.ui_element == lvl1:
                        difficulty = 1
                    if event.ui_element == lvl2:
                        difficulty = 2
                    if event.ui_element == lvl3:
                        difficulty = 3
                    if event.ui_element == lvl4:
                        difficulty = 4
                    if event.ui_element == lvl5:
                        difficulty = 5
                if event.ui_element == shop_button:
                    for i in [lvl1, lvl2, lvl3, lvl4, lvl5, shop_button]:
                        i.disable()
                        i.hide()
                    for i in [buy_speed, buy_slots, exit_button]:
                        i.enable()
                        i.show()
                if event.ui_element == exit_button:
                    for i in [lvl1, lvl2, lvl3, lvl4, lvl5, shop_button]:
                        i.enable()
                        i.show()
                    for i in [buy_speed, buy_slots, exit_button]:
                        i.disable()
                        i.hide()
            manager.process_events(event)
            shop_manager.process_events(event)
        screen.fill((255, 255, 255))
        screen.blit(bg, (0, 0))
        shop_manager.update(time_delta)
        shop_manager.draw_ui(screen)
        manager.update(time_delta)
        manager.draw_ui(screen)
        if buy_speed.is_enabled:
            stats_update(screen, 'Деньги', score, (750, 150))
            stats_update(screen, 'Слотов', f'{backpack_capacity}/3', (850, 390))
            stats_update(screen, 'Скорость', f'{speed // 5 * 100}/300%', (850, 790))
        pygame.display.update()

        guy.set_position((42, 32))
        backpack = []
        mails = []
        for i in range(difficulty * 3):
            mails.append(str(randint(1, 11)))
        mails.sort()

        pygame.time.set_timer(TIMER, 1000)
        if playing:
            pygame.mixer.music.play()
        while playing:
            if time <= 0:
                show_message(screen, 'Вы проиграли')
                pygame.display.flip()
                clock.tick(speed)
                pygame.mixer.music.stop()
                pygame.time.delay(5000)
                playing = False
                time = 60
                pygame.time.set_timer(TIMER, 0)
                continue
            elif len(mails) == 0 and len(backpack) == 0:
                show_message(screen, 'Вы выиграли')
                pygame.display.flip()
                clock.tick(speed)
                pygame.mixer.music.stop()
                pygame.time.delay(5000)
                playing = False
                time = 60
                pygame.time.set_timer(TIMER, 0)
                continue
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    playing = False
                    running = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
                    if level.deliver_mail(guy.get_position(), backpack):
                        score += 10
                    if level.grab_mail(guy.get_position(), mails, backpack, backpack_capacity):
                        pass
                if event.type == TIMER:
                    time -= 1
            game.update_guy()
            screen.fill((0, 0, 0))

            game.render(screen)
            stats_update(screen, 'Деньги', score, (1050, 150))
            stats_update(screen, 'Время', time, (1050, 250))
            stats_update(screen, 'Ожидают доставки', ', '.join(mails), (1050, 350))
            stats_update(screen, 'В рюкзаке', ', '.join(backpack), (1050, 450))

            pygame.display.flip()
            clock.tick(speed)
    pygame.quit()


if __name__ == '__main__':
    main()
