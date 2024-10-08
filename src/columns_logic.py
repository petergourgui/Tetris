import random


class ColumnDoesNotExist(Exception):
    pass

class ExpectedInputMismatch(Exception):
    pass



class ColumnsGame:
    def __init__(self, rows: int, columns: int) -> None:
        'Creates a game with the specified rows and columns, and an empty field.'
        self._rows = rows
        self._columns = columns
        self._faller = None
        self._bottom_faller_row = None
        self._faller_column = None
        self._faller_landed = False
        self._faller_frozen = True
        self._game_over = False

        self._field = []
        for i in range(3):
            self._field.append([])
            for j in range(self._columns):
                self._field[-1].append('   ')
        for i in range(rows):
            self._field.append([])
            for j in range(columns):
                self._field[-1].append('   ')


    def place_contents(self, row: int, input_row: str) -> None:
        'Places jewels at the specified row at the beginning of the game.'
        possible_jewels = ['S', 'T', 'V', 'W', 'X', 'Y', 'Z', ' ']
        if len(input_row) != self._columns:
            raise ExpectedInputMismatch('Input does not match number of columns!')
        
        for character in input_row:
            if character not in possible_jewels:
                raise ExpectedInputMismatch(f'Input must include either only possible jewels or empty space!')
        
        row += 3
        for col in range(self._columns):
            self._field[row][col] = f' {input_row[col]} '

    
    def drop_jewels(self) -> None:
        'Pulls all jewels as far down as possible.'
        jewels_dropped = False
        jewels_dropped = self.drop_once()
        if jewels_dropped:
            self.drop_jewels()


    def process_command(self, command: str) -> None:
        'Performs actions in the game according to the given command.'
        possible_commands = ['', 'R', '<', '>', 'Q']
        if command in possible_commands or (command.startswith('F') and len(command) == 9):
            pass
        else:
            raise ExpectedInputMismatch('Command does not exist!')
        
        if command == '':
            self.remove_matching()
            self.drop_once()
        if command.startswith('F'):
            self.create_faller(command)
        if command == 'R':
            self.rotate_faller()
        if command == '<':
            self.move_faller_left()
        if command == '>':
            self.move_faller_right()
        if command == 'Q':
            quit()


    def create_faller(self, user_input: str) -> None:
        'Creates a new faller and places the bottommost jewel in the field.'
        if self._faller != None or self._jewels_matched():
            return
        
        self._faller_frozen = False
        self._faller_landed = False
        list_input = user_input.split()
        self._faller_column = int(list_input[1]) - 1

        if self._faller_column < 0 or self._faller_column >= self._columns:
            raise ColumnDoesNotExist('Column does not exist in the game field!')
        
        colors = list_input[2:]
        self._bottom_faller_row = 2

        possible_colors = ['S', 'T', 'V', 'W', 'X', 'Y', 'Z']

        if colors[0] in possible_colors and colors[1] in possible_colors and colors[2] in possible_colors:
            pass
        else:
            raise ExpectedInputMismatch('One of the specified jewels does not exist!')

        self._faller = [colors[0], colors[1], colors[2]]
        self._field[0][self._faller_column] = f'[{self._faller[0]}]'
        self._field[1][self._faller_column] = f'[{self._faller[1]}]'
        self._field[2][self._faller_column] = f'[{self._faller[2]}]'
        if self._field[3][self._faller_column] != '   ':
            self._game_over = True
        self.drop_once()


    def create_random_faller(self):
        if self._faller != None or self._jewels_matched():
            return
        
        column_available = False
        for col in range(self._columns):
            if self.game_field()[0][col] == '   ':
                column_available = True

        if not column_available:
            self.create_faller('F 1 S T V')
            return

        column = random.randint(1, self._columns)
        while self.game_field()[0][column - 1] != '   ':
            column = random.randint(1, self._columns)

        column = str(column)
        jewel_colors = ['S', 'T', 'V', 'W', 'X', 'Y', 'Z']
        first_jewel = random.choice(jewel_colors)
        second_jewel = random.choice(jewel_colors)
        third_jewel = random.choice(jewel_colors)

        self.create_faller(f'F {column} {first_jewel} {second_jewel} {third_jewel}')

    
    def _jewels_matched(self) -> bool:
        'Returns True if there are any jewels marked as matched by asterisks. Returns False otherwise.'
        for row in range(self._rows + 3):
            for col in range(self._columns):
                if self._field[row][col].startswith('*'):
                    return True
        return False
        

    def drop_once(self) -> None:
        'Drops all jewels on the field once if possible.'
        jewels_dropped = False
        for row in range(self._rows + 1, -1, -1):
            for col in range(self._columns):
                if self._field[row + 1][col] == '   ' and self._field[row][col] != '   ':
                    self._field[row + 1][col] = self._field[row][col]
                    self._field[row][col] = '   '
                    jewels_dropped = True
        if jewels_dropped and self._faller != None:
            self._bottom_faller_row += 1
            if self._bottom_faller_row + 1 >= self._rows + 3 or self._field[self._bottom_faller_row + 1][self._faller_column] != '   ':
                self._faller_landed = True
                for row in range (self._rows + 3):
                    for col in range(self._columns):
                        if self._field[row][col].startswith('['):
                            self._field[row][col] = f'|{self._field[row][col][1]}|'
        if not jewels_dropped and self._faller_landed:
            self._faller_frozen = True
            self._faller = None
            for row in range (self._rows + 3):
                for col in range(self._columns):
                    if self._field[row][col].startswith('|'):
                        self._field[row][col] = f' {self._field[row][col][1]} '
        if not jewels_dropped and self._faller != None:
            self._faller_landed = True
            for row in range (self._rows + 3):
                for col in range(self._columns):
                    if self._field[row][col].startswith('['):
                        self._field[row][col] = f'|{self._field[row][col][1]}|'

        return jewels_dropped
        

    def rotate_faller(self) -> None:
        'Rotates the current faller in the game field.'
        if self._faller == None:
            return
        
        self._faller = [self._faller[2], self._faller[0], self._faller[1]]
        temp_first = self._field[self._bottom_faller_row][self._faller_column] 
        self._field[self._bottom_faller_row][self._faller_column] = self._field[self._bottom_faller_row - 1][self._faller_column]
        self._field[self._bottom_faller_row - 1][self._faller_column] = self._field[self._bottom_faller_row - 2][self._faller_column]
        self._field[self._bottom_faller_row - 2][self._faller_column] = temp_first


    def move_faller_left(self) -> None:
        'Moves the current faller in the game field to the left if possible.'
        if self._faller == None:
            return
        
        if (self._faller_column - 1) < 0:
            return
        
        space_availabe = True
        for row in range(self._rows + 2, -1, -1):
            if (self._field[row][self._faller_column].startswith('[') or self._field[row][self._faller_column].startswith('|')) and \
                self._field[row][self._faller_column - 1] != '   ':
                space_availabe = False

        if space_availabe:
            self._faller_column = self._faller_column - 1
            for row in range(self._rows + 2, -1, -1):
                if self._field[row][self._faller_column + 1].startswith('[') or self._field[row][self._faller_column + 1].startswith('|'):
                    self._field[row][self._faller_column] = self._field[row][self._faller_column + 1]
                    self._field[row][self._faller_column + 1] = '   '

            space_in_column = False
            index_row = self._find_top_jewel(self._faller_column)
            for row in range(index_row, self._rows + 3):
                if self._field[row][self._faller_column] == '   ':
                    space_in_column = True
            if space_in_column:
                self._faller_landed = False
                for row in range(self._rows + 3):
                    if self._field[row][self._faller_column].startswith('|'):
                        self._field[row][self._faller_column] = f'[{self._field[row][self._faller_column][1]}]'
            else:
                self._faller_landed = True
                for row in range(self._rows + 3):
                    if self._field[row][self._faller_column].startswith('['):
                        self._field[row][self._faller_column] = f'|{self._field[row][self._faller_column][1]}|'


    def _find_top_jewel(self, column: int) -> int:
        'Returns the row number of the first occurence of a jewel in the given column.'
        for row in range(self._rows + 3):
            if self._field[row][column] != '   ':
                return row


    def move_faller_right(self) -> None:
        'Moves the current faller in the game field to the right if possible.'
        if self._faller == None:
            return
        
        if (self._faller_column + 1) >= self._columns:
            return
        
        space_availabe = True
        for row in range(self._rows + 2, -1, -1):
            if (self._field[row][self._faller_column].startswith('[') or self._field[row][self._faller_column].startswith('|')) and \
                self._field[row][self._faller_column + 1] != '   ':
                space_availabe = False

        if space_availabe:
            self._faller_column = self._faller_column + 1
            for row in range(self._rows + 2, -1, -1):
                if self._field[row][self._faller_column - 1].startswith('[') or self._field[row][self._faller_column - 1].startswith('|'):
                    self._field[row][self._faller_column] = self._field[row][self._faller_column - 1]
                    self._field[row][self._faller_column - 1] = '   '

            space_in_column = False
            index_row = self._find_top_jewel(self._faller_column)
            for row in range(index_row, self._rows + 3):
                if self._field[row][self._faller_column] == '   ':
                    space_in_column = True
            if space_in_column:
                self._faller_landed = False
                for row in range(self._rows + 3):
                    if self._field[row][self._faller_column].startswith('|'):
                        self._field[row][self._faller_column] = f'[{self._field[row][self._faller_column][1]}]'
            else:
                self._faller_landed = True
                for row in range(self._rows + 3):
                    if self._field[row][self._faller_column].startswith('['):
                        self._field[row][self._faller_column] = f'|{self._field[row][self._faller_column][1]}|'


    def check_game_over(self) -> None:
        'Ends the game if the faller is frozen and not all of it can fit on the field.'
        if self._faller_frozen:
            for row in self._field:
                for jewel in row:
                    if jewel.startswith('*'):
                        return
            for row in range(3):
                for col in range(self._columns):
                    if self._field[row][col] != '   ':
                        self._game_over = True


    def remove_matching(self) -> None:
        'Removes all jewels that have been identified as matching with other jewels.'
        matches_removed = False
        for row in range(self._rows + 3):
            for col in range(self._columns):
                if self._field[row][col].startswith('*'):
                    self._field[row][col] = '   '
                    matches_removed = True
        if matches_removed:
            self.drop_jewels()


    def check_horizontal_match(self) -> None:
        'Checks if there are three or more jewels matching horizontally and marks them.'
        if self._faller_frozen:
            for row in range(self._rows + 3):
                for col in range(self._columns - 2):
                    if self._field[row][col][1] == self._field[row][col + 1][1] == self._field[row][col + 2][1] and self._field[row][col] != '   ':
                        self._field[row][col] = f'*{self._field[row][col][1]}*'
                        self._field[row][col + 1] = f'*{self._field[row][col][1]}*'
                        self._field[row][col + 2] = f'*{self._field[row][col][1]}*'


    def check_vertical_match(self) -> None:
        'Checks if there are three or more jewels matching vertically and marks them.'
        if self._faller_frozen:
            field_copy = self.field()
            for col in range(self._columns):
                for row in range(self._rows + 1):
                    if field_copy[row][col][1] == field_copy[row + 1][col][1] == field_copy[row + 2][col][1] and field_copy[row][col] != '   ':
                        self._field[row][col] = f'*{field_copy[row][col][1]}*'
                        self._field[row + 1][col] = f'*{field_copy[row][col][1]}*'
                        self._field[row + 2][col] = f'*{field_copy[row][col][1]}*'
    

    def check_diagonal_match(self) -> None:
        'Checks if there are three or more jewels matching diagonally and marks them.'
        self._diagonal_right_down()
        self._diagonal_left_down()


    def _diagonal_right_down(self) -> None:
        'Checks if there are three or more jewels matching diagonally to the right downwards.'
        if self._faller_frozen:
            field_copy = self.field()
            for row in range(self._rows + 1):
                for col in range(self._columns - 2):
                    if self._field[row][col][1] == field_copy[row + 1][col + 1][1] == field_copy[row + 2][col + 2][1] and field_copy[row][col] != '   ':
                        self._field[row][col] = f'*{field_copy[row][col][1]}*'
                        self._field[row + 1][col + 1] = f'*{field_copy[row + 1][col + 1][1]}*'
                        self._field[row + 2][col + 2] = f'*{field_copy[row + 2][col + 2][1]}*'

    
    def _diagonal_left_down(self) -> None:
        'Checks if there are three or more jewels matching diagonally to the left downwards.'
        if self._faller_frozen:
            field_copy = self.field()
            for row in range(self._rows + 1):
                for col in range(2, self._columns):
                    if self._field[row][col][1] == field_copy[row + 1][col - 1][1] == field_copy[row + 2][col - 2][1] and field_copy[row][col] != '   ':
                        self._field[row][col] = f'*{field_copy[row][col][1]}*'
                        self._field[row + 1][col - 1] = f'*{field_copy[row + 1][col - 1][1]}*'
                        self._field[row + 2][col - 2] = f'*{field_copy[row + 2][col - 2][1]}*'


    def game_over(self) -> bool:
        'Returns the a boolean representing whether the game is over or not.'
        return self._game_over
    

    def rows(self) -> int:
        'Returns the number of rows in the field.'
        return self._rows
    
    
    def columns(self) -> int:
        'Returns the number of columsn in the field.'
        return self._columns
    
    
    def field(self) -> list[list]:
        'Returns the 2D list reprenting the field including fallers outside the game field.'
        return self._field.copy()
    
    
    def game_field(self) -> list[list]:
        'Return the 2D list representing the game field without any fallers that are outside the game field.'
        field_copy = self._field.copy()
        field_copy = field_copy[3:]
        return field_copy
    

    def get_faller(self) -> list[list]:
        'Returns the current faller in the game field.'
        return self._faller.copy()
    

    def faller_landed(self):
        return self._faller_landed