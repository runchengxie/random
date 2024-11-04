import curses
import random

def main(stdscr):
    # Initialize the screen
    curses.curs_set(0)  # type: ignore
    sh, sw = stdscr.getmaxyx()
    w = curses.newwin(sh, sw, 0, 0)  # type: ignore
    w.keypad(1)
    w.timeout(100)
    w.border(0)  # Add border

    # Initial position of the snake
    snk_x = sw // 4
    snk_y = sh // 2
    snake = [
        [snk_y, snk_x],
        [snk_y, snk_x - 1],
        [snk_y, snk_x - 2]
    ]

    # Initial position of the food
    food = [sh // 2, sw // 2]
    w.addch(int(food[0]), int(food[1]), curses.ACS_PI)  # type: ignore

    key = curses.KEY_RIGHT  # type: ignore

    while True:
        next_key = w.getch()
        key = key if next_key == -1 else next_key

        # Check if the snake hits the border or itself
        if snake[0][0] in [0, sh - 1] or \
           snake[0][1] in [0, sw - 1] or \
           snake[0] in snake[1:]:
            curses.endwin()  # type: ignore
            quit()

        # Calculate the new head of the snake
        new_head = [snake[0][0], snake[0][1]]

        # Move the snake towards the food
        if snake[0][0] < food[0]:
            new_head[0] += 1
        elif snake[0][0] > food[0]:
            new_head[0] -= 1
        elif snake[0][1] < food[1]:
            new_head[1] += 1
        elif snake[0][1] > food[1]:
            new_head[1] -= 1

        snake.insert(0, new_head)

        # Check if the snake has eaten the food
        if snake[0] == food:
            food = None
            while food is None:
                nf = [
                    random.randint(1, sh - 2),
                    random.randint(1, sw - 2)
                ]
                food = nf if nf not in snake else None
            w.addch(food[0], food[1], curses.ACS_PI)  # type: ignore
        else:
            tail = snake.pop()
            w.addch(int(tail[0]), int(tail[1]), ' ')

        w.addch(int(snake[0][0]), int(snake[0][1]), curses.ACS_CKBOARD)  # type: ignore

if __name__ == "__main__":
    curses.wrapper(main)  # type: ignore