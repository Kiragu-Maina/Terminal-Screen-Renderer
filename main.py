import curses
import struct

# Command identifiers: These constants represent the commands used in the binary stream.
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
        # Ensure enough data is present for a valid command and its length byte
        if i + 1 >= len(stream):  
            raise ValueError(f"Malformed stream at index {i}: insufficient data for length.")
        
        command = stream[i]  # Read the command identifier
        length = stream[i + 1]  # Read the length of the data associated with the command
        
        # Validate if the stream contains sufficient data as declared by the length byte
        if i + 2 + length > len(stream):
            raise ValueError(f"Malformed stream at index {i}: insufficient data for command {command}.")
        
        data = stream[i + 2: i + 2 + length]  # Extract the command's data
        yield command, data  # Yield the command and its data as a tuple
        i += 2 + length  # Move the pointer to the next command in the stream

def setup_screen(data):
    """Handle screen setup command."""
    width, height, color_mode = data  # Extract screen dimensions and color mode
    return width, height, color_mode  # Return the parsed setup information

def draw_char(screen, data):
    """Handle drawing a character."""
    x, y, color, char = data  # Extract position, color, and character information
    screen.addch(y, x, char)  # Draw the character on the screen at the specified position

def draw_line(screen, data):
    """Handle drawing a line between two points."""
    x1, y1, x2, y2, color, char = data  # Extract start and end points, color, and character
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    sx = 1 if x1 < x2 else -1  # Determine x step direction
    sy = 1 if y1 < y2 else -1  # Determine y step direction
    err = dx - dy

    max_y, max_x = screen.getmaxyx()  # Get screen dimensions to avoid out-of-bound errors
    while True:
        if 0 <= y1 < max_y and 0 <= x1 < max_x:
            screen.addch(y1, x1, char)  # Draw the character at the current position
        if x1 == x2 and y1 == y2:  # Break loop when the endpoint is reached
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
    x, y, color, *text = data  # Extract position, color, and text data
    for i, char in enumerate(text):  # Loop through each character in the text
        screen.addch(y, x + i, char)  # Render each character at the specified position

def move_cursor(screen, data):
    """Move the cursor to a specific location."""
    x, y = data  # Extract cursor position
    screen.move(y, x)  # Move the cursor to the specified position

def draw_at_cursor(screen, data):
    """Draw a character at the current cursor location."""
    char, color = data  # Extract character and color information
    y, x = screen.getyx()  # Get the current cursor position
    screen.addch(y, x, char)  # Draw the character at the cursor's position

def clear_screen(screen):
    """Clear the screen."""
    screen.clear()  # Clear all content from the screen

def render_terminal(screen, commands):
    """Render commands to the terminal screen."""
    screen.clear()  # Clear the screen before rendering
    dimensions_set = False  # Ensure screen dimensions are set before rendering commands
    for command, data in commands:
        if command == COMMAND_SETUP:
            width, height, color_mode = setup_screen(data)  # Setup screen dimensions and color mode
            screen.clear()  # Clear screen after setup
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
            break  # Stop processing commands
        screen.refresh()  # Refresh the screen to reflect the changes
    screen.getch()  # Wait for user input to prevent immediate closure

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
    commands = parse_binary_stream(binary_stream)  # Parse the binary stream into commands
    curses.wrapper(lambda stdscr: render_terminal(stdscr, commands))  # Render commands in a terminal-safe wrapper

if __name__ == "__main__":
    main()  # Run the main function
