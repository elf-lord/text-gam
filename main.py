import curses
from curses import window
import traceback
import json
import os

class Choice:
    def __init__(self, next_id: int, answer: str):
        self.next_id = next_id
        self.answer = answer

class DialogueNode:
    def __init__(self, info: dict):
        self.id = info['id']
        self.character = info['character']
        self.phrase = info['phrase']
        self.art = info['art']
        self.is_ending = info['is_ending']
        self.choices: list[Choice] = list()
        for c in info['choices']:
            self.choices.append(Choice(c['next_id'], c['answer']))


def read_dialogues_from_file(filename: str) -> dict[int, DialogueNode]:
    dialogues_json: json = None
    with open(filename, 'r') as fp:
        dialogues_json = json.load(fp)

    dialogues: dict[int, DialogueNode] = dict()
    for d in dialogues_json:
        dialogues[d['id']] = DialogueNode(d)

    return dialogues


def curses_begin(stdscr: window):
    curses.noecho()
    curses.cbreak()
    stdscr.keypad(True)
    curses.curs_set(False)


def curses_end(stdscr: window):
    stdscr.keypad(False)
    curses.echo()
    curses.nocbreak()
    curses.curs_set(True)
    curses.endwin()


def load_assets(asset_folder: str) -> dict[str, str]:
    assets = dict()

    for filename in os.listdir(asset_folder):
        file_path = os.path.join(asset_folder, filename)
        print(f'trying to read file: {filename}')
        if os.path.isfile(file_path):
            with open(file_path, "r", encoding="utf-8") as fp:
                assets[filename] = fp.read()
    return assets



def main(stdscr: window):
    assets = load_assets('assets')
    window_should_close = False
    dialogues: dict[int, DialogueNode]
    dialogues = read_dialogues_from_file('dialogues.json')

    current_node: DialogueNode = dialogues[0]

    while not window_should_close:
        stdscr.clear()
        art_asset = assets.get(current_node.art, '')
        if current_node.is_ending:
            stdscr.addstr(art_asset)
            stdscr.addstr("Press q to exit", curses.A_BOLD | curses.A_UNDERLINE)
        else:
            stdscr.addstr(art_asset)
            stdscr.addstr(current_node.character, curses.A_BOLD)
            stdscr.addstr('\n')
            stdscr.addstr(current_node.phrase)
            stdscr.addstr('\n')
            stdscr.addstr('-' * 10)
            stdscr.addstr('\n')
            for i, choice in enumerate(current_node.choices):
                stdscr.addstr(f'{i + 1}: {choice.answer}\n')

        c = chr(stdscr.getch())
        if c == 'q':
            window_should_close = True
        if c.isdecimal() and int(c) >= 1 and int(c) <= len(current_node.choices):
            choice = current_node.choices[int(c) - 1]
            current_node = dialogues[choice.next_id]

        stdscr.refresh()



if __name__ == '__main__':
    stdscr = curses.initscr()
    curses_begin(stdscr)

    try:
        main(stdscr)
    except Exception as e:
        curses_end(stdscr)
        print(f'An error occured: {e}')
        traceback.print_exc()
    else:
        curses_end(stdscr)



