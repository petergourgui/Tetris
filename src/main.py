import pygame
import columns_logic


_FRAME_RATE = 30
_INITIAL_WIDTH = 450
_INITIAL_HEIGHT = 850
_BACKGROUND_COLOR = pygame.Color(0, 0, 0) # Black
_S_COLOR = pygame.Color(255, 0, 0) # Red
_T_COLOR = pygame.Color(252, 132, 3) # Orange
_V_COLOR = pygame.Color(236, 252, 3) # Yellow
_W_COLOR = pygame.Color(57, 252, 3) # Green
_X_COLOR = pygame.Color(3, 248, 252) # Light Blue
_Y_COLOR = pygame.Color(28, 0, 252) # Dark Blue
_Z_COLOR = pygame.Color(252, 0, 231) # Pink
_FALLER_LANDED_COLOR = pygame.Color(75, 75, 75) # Gray
_MATCHING_COLOR = pygame.Color(255, 255, 255) # White
_NUM_ROWS = 13
_NUM_COLUMNS = 6
_COLUMN_WIDTH = 1 / _NUM_COLUMNS
_ROW_HEIGHT = 1 / _NUM_ROWS


class ColumnsGUI:
    def __init__(self):
        self._game = columns_logic.ColumnsGame(_NUM_ROWS, _NUM_COLUMNS)
        self._running = True


    def run(self) -> None:
        'Runs the game from start to finish'
        pygame.init()

        try:
            clock = pygame.time.Clock()
            frame_cycle = 0
            self._create_surface((_INITIAL_WIDTH, _INITIAL_HEIGHT))

            while self._running:
                clock.tick(_FRAME_RATE)
                if frame_cycle % _FRAME_RATE == 0:
                    frame_cycle = 0
                    self._game.process_command('')
                    self._game.check_horizontal_match()
                    self._game.check_vertical_match()
                    self._game.check_diagonal_match()
                    self._game.check_game_over()
                    if self._game.game_over():
                        break
                    self._game.create_random_faller()
                    
                self._handle_events()
                self._draw_frame()
                frame_cycle += 1

            while self._game.game_over() and self._running:
                self._surface.fill(_BACKGROUND_COLOR)
                self._draw_game_over()
                self._handle_events()
            
        finally:
            pygame.quit()


    def _create_surface(self, size: tuple[int, int]) -> None:
        'Creates a pygame surface to display the game on'
        self._surface = pygame.display.set_mode(size, pygame.RESIZABLE)


    def _handle_events(self) -> None:
        'Handles all events that the user made since last checked'
        for event in pygame.event.get():
            self._handle_event(event)


    def _handle_event(self, event) -> None:
        'Quits the game if the user exits. Resizes the window if the user resizes it.'
        if event.type == pygame.QUIT:
            self._stop_running()
        elif event.type == pygame.VIDEORESIZE:
            self._create_surface(event.size)
        elif event.type == pygame.KEYDOWN:
            self._handle_keys()
            

    def _handle_keys(self) -> None:
        'Handles all possible keys that could be pressed in the game'
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT]:
            self._game.move_faller_left()

        if keys[pygame.K_RIGHT]:
            self._game.move_faller_right()

        if keys[pygame.K_SPACE]:
            self._game.rotate_faller()


    def _stop_running(self) -> None:
        'Stops running the game.'
        self._running = False


    def _draw_game_over(self) -> None:
        'Displays a game over screen.'
        font = pygame.font.Font('freesansbold.ttf', int(0.1 * self._surface.get_width()))
        text = font.render('GAME OVER', True, (255, 0, 0), (0, 200, 50))
        text_rect = text.get_rect()
        text_rect.center = (self._surface.get_width() // 2, self._surface.get_height() // 2)
        self._surface.blit(text, text_rect)
        pygame.display.flip()


    def _draw_frame(self) -> None:
        'Draws the current game state.'
        self._surface.fill(_BACKGROUND_COLOR)

        game_field = self._game.game_field()
        for row in range(_NUM_ROWS):
            for col in range(_NUM_COLUMNS):
                top_left_frac_x = col / _NUM_COLUMNS
                top_left_frac_y = row / _NUM_ROWS

                top_left_pixel_x = self._frac_x_to_pixel_x(top_left_frac_x)
                top_left_pixel_y = self._frac_y_to_pixel_y(top_left_frac_y)

                rect_width_pixel = self._frac_x_to_pixel_x(_COLUMN_WIDTH)
                rect_height_pixel = self._frac_y_to_pixel_y(_ROW_HEIGHT)

                self._draw_jewel(game_field[row][col], top_left_pixel_x, top_left_pixel_y, \
                                 rect_width_pixel, rect_height_pixel)
                
        pygame.display.flip()


    def _draw_jewel(self, jewel_letter: str, pixel_x: int, pixel_y: int, width: int, height: int):
        'Draws a jewel in the given position and according to what jewel letter it is.'
        jewel_rect = pygame.Rect(pixel_x, pixel_y, width, height)
        
        if jewel_letter.startswith('|'):
            pygame.draw.rect(self._surface, _FALLER_LANDED_COLOR, jewel_rect)

        if jewel_letter.startswith('*'):
            pygame.draw.rect(self._surface, _MATCHING_COLOR, jewel_rect)
            
        if jewel_letter[1] == 'S':
            pygame.draw.ellipse(self._surface, _S_COLOR, jewel_rect)

        if jewel_letter[1] == 'T':
            pygame.draw.ellipse(self._surface, _T_COLOR, jewel_rect)

        if jewel_letter[1] == 'V':
            pygame.draw.ellipse(self._surface, _V_COLOR, jewel_rect)

        if jewel_letter[1] == 'W':
            pygame.draw.ellipse(self._surface, _W_COLOR, jewel_rect)

        if jewel_letter[1] == 'X':
            pygame.draw.ellipse(self._surface, _X_COLOR, jewel_rect)

        if jewel_letter[1] == 'Y':
            pygame.draw.ellipse(self._surface, _Y_COLOR, jewel_rect)

        if jewel_letter[1] == 'Z':
            pygame.draw.ellipse(self._surface, _Z_COLOR, jewel_rect)
        

    def _frac_x_to_pixel_x(self, frac_x: float) -> int:
        'Converts a fractional x-coordinate to a pixel x-coordinate.'
        return self._frac_to_pixel(frac_x, self._surface.get_width())


    def _frac_y_to_pixel_y(self, frac_y: float) -> int:
        'Converts a fractional y-coordinate to a pixel y-coordinate.'
        return self._frac_to_pixel(frac_y, self._surface.get_height())


    def _frac_to_pixel(self, frac: float, max_pixel: int) -> int:
        'Converts the given fraction to a pixel coordinate.'
        return int(frac * max_pixel)


if __name__ == '__main__':
    ColumnsGUI().run()
