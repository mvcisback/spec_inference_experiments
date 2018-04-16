#!/usr/bin/env python

import csv
import time
import subprocess
import random
from pathlib import Path
from collections import namedtuple
from enum import Enum
from tempfile import NamedTemporaryFile

import click
from blessings import Terminal
from lenses import lens, bind

TERM = Terminal()
GOAL = "Enter and stay in both of the black regions for 4 time steps.\n"
DIED = "☠"
POS = "▣"
CHAR_PER_ROW = 16
EMPTY_BOARD = """
■ ■ ■ ■ ■ ■ ■ ■
■ ■ ■ ■ ■ ■ ■ ■
■ ■ ■ ■ ■ ■ ■ ■
■ ■ ■ ■ ■ ■ ■ ■
■ ■ ■ ■ ■ ■ ■ ■
■ ■ ■ ■ ■ ■ ■ ■
■ ■ ■ ■ ■ ■ ■ ■
■ ■ ■ ■ ■ ■ ■ ■
""" [1:]

State = namedtuple("State", ["x", "y", "failed"])

class Action(Enum):
    N = 0
    NE = 1
    E = 2
    SE = 3
    S = 4
    SW = 5
    W = 6
    NW = 7
    STAY = (0, 0)

def flat_index(y, x):
    return CHAR_PER_ROW * x + 2 * y

def update_board(s: State, b=EMPTY_BOARD):
    with NamedTemporaryFile("w") as f:
        f.write(to_sense_stim(s))
        f.flush()
        out = subprocess.check_output(f"aigsim -m sense.aig {f.name}", shell=True)
    
    colorize = unpack_sense_stim_result(out)

    cursor = colorize(POS)
    board = bind(b)[flat_index(s.x, s.y)].set(cursor)
    return board


PROMPT = """\
Actions:
NW  N  NE
W       E
SW  S  SE

Type Input Followed by Enter: """


def show_board(t, s: State, b=EMPTY_BOARD):
    s = State(s.x, 7 - s.y, s.failed)
    board = update_board(s, b)
    print(f"{TERM.clear()}{GOAL}\nTime: {t}/{17-1}\n\n{board}\n\n{PROMPT}")


def steps(controller, rounds=17):
    """TODO: use edge length"""
    x0, y0 = random.randrange(0, 7), random.randrange(0, 7)
    s = State(x0, y0, False)
    next(controller)
    for i in range(rounds):
        yield s
        a = controller.send(s)
        s = move(s, a)


def unpack_stim_result(out):
    xy = out.splitlines()[0].split()[1]
    return int(xy[:3],2), int(xy[3:],2)


# Necessary because of magic TERM object does.
COLORIZE = (
    lambda x: TERM.blue(x),
    lambda x: TERM.yellow(x),
    lambda x: TERM.magenta(x),
    lambda x: TERM.red(x),
    lambda x: x,
)


def unpack_sense_stim_result(out):
    val = out.splitlines()[0].split()[1]
    if val.count(b'1') > 1:
        raise RuntimeError("unexpected sensor value")
    idx = 4 if val.count(b'1') == 0 else val.index(b'1')
    return COLORIZE[idx]


def deterministic_move(s: State, a: Action, n=8):
    with NamedTemporaryFile("w") as f:
        f.write(to_stim(s, a))
        f.flush()
        out = subprocess.check_output(f"aigsim -m step2d.aig {f.name}", shell=True)
    
    x, y = unpack_stim_result(out)

    # TODO: when lava added
    failed = s.failed
    
    return State(x, y, failed)


def to_stim(s: State, a: Action):
    return f"{s.x:03b}{s.y:03b}{a.value:03b}\n."

def to_sense_stim(s: State):
    return f"{s.x:03b}{7-s.y:03b}\n."


def move(s: State, a: Action, n=8):
    if s.failed:
        return s
    return deterministic_move(s, a, n)


def human():
    yield
    while True:
        try:
            a_str = input().upper().strip()
            yield getattr(Action, a_str)
        except AttributeError:
            continue


@click.command()
@click.argument('data_dir', type=click.Path(exists=True,
                                            dir_okay=True, file_okay=False))
@click.option('--n_samples', type=click.IntRange(0, 2**10), default=30)
def main(data_dir, n_samples):
    root = Path(data_dir)
    paths = (root / f"run_{i}.csv" for i in range(n_samples))
    for path in paths:
        with path.open('w') as fp:
            writer = csv.writer(fp)
            writer.writerow(["x", "y", "failed"])
            trace = steps(human())
            for i, s in enumerate(trace):
                show_board(i, s)
                writer.writerow([s.x, s.y, s.failed])


if __name__ == '__main__':
    main()
