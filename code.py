from adafruit_circuitplayground import cp
import time
import random
from adafruit_neotrellis.neotrellis import NeoTrellis
import board, busio

i2c = busio.I2C(board.SCL, board.SDA)
trellis = NeoTrellis(i2c)
trellis.pixels.brightness = 0.15

callbacks = [None] * 16

def wait_for_start_or_quit():
    print('Press Button A to start, Button B to quit')
    cp.pixels.fill((0,0,50))

    while True:
        if cp.button_a:
            return "start"
        if cp.button_b:
            return "quit"
        time.sleep(0.05)

sequence = []
user_input = []
score = 0
game_over = False
waiting_for_input = False

def flash_tile(x, y, color=(0, 255, 0), duration=0.4):
    idx = y * 4 + x
    trellis.pixels[idx] = color
    time.sleep(duration)
    trellis.pixels[idx] = (0, 0, 0)
    time.sleep(0.15)

def show_sequence():
    for x, y in sequence:
        flash_tile(x, y)

def reset_board():
    for i in range(16):
        trellis.pixels[i] = (0, 0, 0)

def key_event(x, y, edge):
    global waiting_for_input, user_input, game_over

    if not waiting_for_input:
        return

    if edge != NeoTrellis.EDGE_RISING:
        return

    print("Pressed: ", y * 4 + x)
    cp.play_tone(200, 0.25)
    flash_tile(x, y, (0, 0, 255), 0.2)
    user_input.append((x, y))

    index = len(user_input) - 1
    if user_input[index] != sequence[index]:
        game_over = True
        waiting_for_input = False

def trellis_callback(event):
    if event.edge != NeoTrellis.EDGE_RISING:
        return
    if not waiting_for_input:
        return

    key = event.number
    x = key % 4
    y = key // 4
    key_event(x, y, event.edge)

def enable_keys():
    for i in range(16):
        trellis.activate_key(i, NeoTrellis.EDGE_RISING)
        trellis.callbacks[i] = trellis_callback

def disable_keys():
    for i in range(16):
        trellis.callbacks[i] = None
        trellis.activate_key(i, 0)

enable_keys()

while True:
    choice = wait_for_start_or_quit()

    if choice == "quit":
        cp.pixels.fill((0,0,0))
        print("Game End.")
        break

    cp.pixels.fill((0,0,0))
    reset_board()
    sequence = []
    user_input = []
    score = 0
    game_over = False
    waiting_for_input = False

    while not game_over:
        print("Next Input")
        sequence.append((random.randint(0,3), random.randint(0,3)))
        user_input = []

        disable_keys()
        waiting_for_input = False

        time.sleep(0.5)
        show_sequence()

        # All green flash
        for i in range(16):
            trellis.pixels[i] = (0, 255, 0)
        time.sleep(0.3)
        reset_board()

        enable_keys()
        waiting_for_input = True
        round_start_time = time.monotonic()

        user_input = []

        while waiting_for_input and not game_over:
            trellis.sync()
            time.sleep(0.02)

            if len(user_input) == len(sequence):
                waiting_for_input = False

        if (len(user_input) == len(sequence)) and user_input[-1] == sequence[-1]:
            score = len(sequence)
            disable_keys()

        if game_over:
            print(f"Game Over! Final Score: {score}")
            for _ in range(3):
                for i in range(16):
                    trellis.pixels[i] = (100,0,0)
                time.sleep(0.3)
                reset_board()
                time.sleep(0.3)
            break

        time.sleep(0.5)

# Final game over animation
for _ in range(3):
    for i in range(16):
        trellis.pixels[i] = (100,0,0)
    time.sleep(0.3)
    reset_board()
    time.sleep(0.3)
