import curses
import struct

# Command identifiers
COMMAND_SETUP = 0x1
COMMAND_DRAW_CHAR = 0x2
COMMAND_DRAW_LINE = 0x3
COMMAND_RENDER_TEXT = 0x4
COMMAND_MOVE_CURSOR = 0x5
COMMAND_DRAW_AT_CURSOR = 0x6
COMMAND_CLEAR_SCREEN = 0x7
COMMAND_END = 0xFF

def parse_binary_stream(stream):
    """Parse a binary stream into commands and associated data."""
    i = 0
    while i < len(stream):
        # print(f"Parsing index {i}...")
        if i + 1 >= len(stream):  # Ensure enough data for command and length
            raise ValueError(f"Malformed stream at index {i}: insufficient data for length.")
        
        command = stream[i]
        length = stream[i + 1]
        
        if i + 2 + length > len(stream):  # Ensure enough data for the declared length
            raise ValueError(f"Malformed stream at index {i}: insufficient data for command {command}.")
        
        data = stream[i + 2: i + 2 + length]
        # print(f"Command: {command}, Length: {length}, Data: {data}")
        yield command, data
        i += 2 + length

def setup_screen(data):
    """Handle screen setup command."""
    width, height, color_mode = data
    # print(f"Setup screen: width={width}, height={height}, color_mode={color_mode}")
    return width, height, color_mode

def draw_char(screen, data):
    """Handle drawing a character."""
    x, y, color, char = data
    # print(f"Draw char '{chr(char)}' at ({x}, {y}) with color {color}")
    screen.addch(y, x, char)

def draw_line(screen, data):
    """Handle drawing a line between two points."""
    x1, y1, x2, y2, color, char = data
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    sx = 1 if x1 < x2 else -1
    sy = 1 if y1 < y2 else -1
    err = dx - dy

    max_y, max_x = screen.getmaxyx()
    # print(f"Draw line from ({x1}, {y1}) to ({x2}, {y2}) with char '{chr(char)}' and color {color}")
    while True:
        if 0 <= y1 < max_y and 0 <= x1 < max_x:
            screen.addch(y1, x1, char)
        if x1 == x2 and y1 == y2:
            break
        e2 = err * 2
        if e2 > -dy:
            err -= dy
            x1 += sx
        if e2 < dx:
            err += dx
            y1 += sy

def render_text(screen, data):
    """Handle rendering a string of text."""
    x, y, color, *text = data
    # print(f"Render text '{''.join(map(chr, text))}' at ({x}, {y}) with color {color}")
    for i, char in enumerate(text):
        screen.addch(y, x + i, char)

def move_cursor(screen, data):
    """Move the cursor to a specific location."""
    x, y = data
    # print(f"Move cursor to ({x}, {y})")
    screen.move(y, x)

def draw_at_cursor(screen, data):
    """Draw a character at the current cursor location."""
    char, color = data
    y, x = screen.getyx()
    # print(f"Draw char '{chr(char)}' at cursor ({x}, {y}) with color {color}")
    screen.addch(y, x, char)

def clear_screen(screen):
    """Clear the screen."""
    # print("Clear screen")
    screen.clear()

def render_terminal(screen, commands):
    """Render commands to the terminal screen."""
    screen.clear()
    dimensions_set = False
    for command, data in commands:
        if command == COMMAND_SETUP:
            width, height, color_mode = setup_screen(data)
            screen.clear()
            dimensions_set = True
        elif not dimensions_set:
            raise ValueError("Screen dimensions must be set before any other commands!")
        elif command == COMMAND_DRAW_CHAR:
            draw_char(screen, data)
        elif command == COMMAND_DRAW_LINE:
            draw_line(screen, data)
        elif command == COMMAND_RENDER_TEXT:
            render_text(screen, data)
        elif command == COMMAND_MOVE_CURSOR:
            move_cursor(screen, data)
        elif command == COMMAND_DRAW_AT_CURSOR:
            draw_at_cursor(screen, data)
        elif command == COMMAND_CLEAR_SCREEN:
            clear_screen(screen)
        elif command == COMMAND_END:
            # print("End of commands")
            break
        screen.refresh()
    screen.getch()  # Pause for user to view output

def main():
    """Main program logic."""
    binary_stream = bytearray([
        COMMAND_SETUP, 3, 30, 20, 0x01,            # Set up a 40x20 screen
        COMMAND_DRAW_CHAR, 4, 5, 5, 0x02, ord('A'), # Draw 'A' at (5, 5)
        COMMAND_DRAW_LINE, 6, 10, 10, 20, 10, 0x02, ord('-'),  # Draw a line
        COMMAND_RENDER_TEXT, 6, 3, 3, 0x02, ord('H'), ord('i'), ord('!'), # Render text
        COMMAND_MOVE_CURSOR, 2, 15, 5,             # Move cursor to (15, 5)
        COMMAND_DRAW_AT_CURSOR, 2, ord('*'), 0x02, # Draw '*' at cursor
        COMMAND_END, 0                             # End commands
    ])
    commands = parse_binary_stream(binary_stream)
    curses.wrapper(lambda stdscr: render_terminal(stdscr, commands))

if __name__ == "__main__":
    main()
