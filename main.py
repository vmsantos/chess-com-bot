from selenium import webdriver
import time
import chess
import chess.engine
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options

engine = chess.engine.SimpleEngine.popen_uci("/usr/games/stockfish")


class Piece:
    def __init__(self, type, colour, x, y):
        self.type = type
        self.colour = colour


def start_bot_game():
    chrome_options = Options()
    chrome_options.add_experimental_option("prefs", {
        "profile.default_content_setting_values.notifications": 2
    })
    chrome_options.add_argument("--start-maximized")

    driver = webdriver.Chrome(options=chrome_options)
    url = 'https://www.chess.com/login'
    driver.get(url)
    time.sleep(2)

    username = driver.find_elements_by_xpath("/html/body/div[1]/div/main/div[1]/form/div[1]/input")[0]
    username.send_keys("username")
    time.sleep(0.5)
    password = driver.find_elements_by_xpath("/html/body/div[1]/div/main/div[1]/form/div[2]/input")[0]
    password.send_keys("password")
    password.send_keys(Keys.RETURN)
        time.sleep(1)
    url = 'https://www.chess.com/play/computer'
    driver.get(url)
    time.sleep(2)
    popup = driver.find_elements_by_xpath("/html/body/div[1]/div[5]/div/div[2]/div[2]/span")
    if popup:
        popup[0].click()
    time.sleep(2)
    WebDriverWait(driver, 20).until(expected_conditions.presence_of_element_located(
        (By.XPATH, "/html/body/div[2]/div[7]/div/div/span")))
    button = driver.find_elements_by_xpath("/html/body/div[2]/div[7]/div/div/span")[0]
    button.click()
    time.sleep(2)
    driver.refresh()
    time.sleep(1)
    button = driver.find_elements_by_xpath("//*[contains(text(), 'Choose')]")
    button[0].click()
    time.sleep(1)
    driver.find_elements_by_xpath("/html/body/div[4]/div[1]/section/div/div[2]/div[1]/div/div[1]/div/span[1]")[
        0].click()
    time.sleep(1)
    #button = driver.find_elements_by_xpath("/html/body/div[14]/div/div/button")
    #button[0].click()

    button = driver.find_elements_by_xpath("/html/body/div[4]/div[1]/div[2]/button")
    button[0].click()

    time.sleep(2)
    return driver


def display_board(game):
    time.sleep(1)
    game.find_elements_by_class_name("download")[0].click()
    WebDriverWait(game, 20).until(expected_conditions.presence_of_element_located(
        (By.XPATH, "/html/body/div[2]/div[5]/div/div[2]/div[2]/div/section/div[3]")))

    fen_element = game.find_elements_by_xpath("/html/body/div[2]/div[5]/div/div[2]/div[2]/div/section/div[3]")[0]
    fen = fen_element.get_attribute("fen")
    board = chess.Board()
    board.set_fen(fen)
    print(board)
    time.sleep(1)
    game.find_elements_by_xpath("/html/body/div[2]/div[5]/div/div[2]/div[1]/span")[0].click()
    return [game, board]


def get_element_by_board_cords(game, x, y):
    chess_board = game.find_elements_by_xpath("//chess-board")[0].rect
    square_height = int(chess_board["height"]) / 8
    x = square_height * x
    y = int(chess_board["height"]) - (square_height * y)
    return (x, y)


def translate(input):
    map = [
        [0, 8, 16, 24, 32, 40, 48, 56],
        [1, 9, 17, 25, 33, 41, 49, 57],
        [2, 10, 18, 26, 34, 42, 50, 58],
        [3, 11, 19, 27, 35, 43, 51, 59],
        [4, 12, 20, 28, 36, 44, 52, 60],
        [5, 13, 21, 29, 37, 45, 53, 61],
        [6, 14, 22, 30, 38, 46, 54, 62],
        [7, 15, 23, 31, 39, 47, 55, 63]
    ]
    for i in range(8):
        for j in range(8):
            if input == map[i][j]:
                return (i + 1, j + 1)
    # i 1=1, 2


def move(game, board):
    original_game = game
    original_board = board
    # predict move
    board.set_fen(display_board(game)[1].fen())
    if not chess.Color(chess.WHITE) or board.is_game_over():
        return game, board
    result = engine.play(board, chess.engine.Limit(time=1))
    board.push(result.move)
    print(result.move)
    print("from ", result.move.from_square)
    print("to ", result.move.to_square)
    from_square_x, from_square_y = translate(result.move.from_square)
    to_square_x, to_square_y = translate(result.move.to_square)
    print("translated:", "square-" + str(from_square_x) + str(from_square_y))

    WebDriverWait(game, 20).until(expected_conditions.presence_of_element_located(
        (By.CLASS_NAME, "square-" + str(from_square_x) + str(from_square_y))))
    game.find_elements_by_class_name("square-" + str(from_square_x) + str(from_square_y))[0].click()
    time.sleep(1.5)
    action = ActionChains(game)
    clickable = game.find_elements_by_class_name("coordinates")[0]
    x, y = get_element_by_board_cords(game, to_square_x, to_square_y)
    action.move_to_element_with_offset(clickable, x, y)
    action.click()
    action.perform()
    time.sleep(1.5)
    if board.fen() != display_board(game)[1].fen():
        move(original_game, original_board)
    return game, board


def play_game(game, board, colour):
    if colour == 'white':
        # make first move
        game, board = move(game, board)
        time.sleep(5)
    while not board.is_game_over():
        time.sleep(5)
        print("Waiting for other player!")
        if chess.Color(chess.WHITE):
            print("it is white's turn")
            game, board = move(game, board)


game = start_bot_game()
print("waiting for game to begin")
time.sleep(5)
print("lets go!")
game, board = display_board(game)
# what colour are we?
if game.find_elements_by_xpath("/html/body/div[2]/chess-board/div[2]")[0].get_attribute("class").split()[1][0] == "w":
    play_game(game, board, 'white')
else:
    play_game(game, board, 'black')

print("victory royale, dub well caught")
game.quit()
