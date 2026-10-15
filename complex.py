"""Do not grade! Entirely generated with AI just as an experiment."""

import shutil
import sys
import textwrap
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import NotRequired, TypedDict

import json5
import questionary
from questionary import Choice, Separator, Style

STORY_PATH = Path(__file__).with_name("story-simple.jsonc")
DEFAULT_NAME = "Traveler"
REMINDER_EVERY = 4
MAX_TEXT_WIDTH = 72
ART_WIDTH = 37

ENDING_PROMISES = (
    "The narrator promises that an ending is just beyond the next door.",
    "The narrator repeats the promise, with less confidence this time.",
    "The ending is still promised. No arrival time is available.",
)

PROMPT_STYLE = Style(
    [
        ("qmark", "fg:ansicyan bold"),
        ("question", "bold"),
        ("pointer", "fg:ansicyan bold"),
        ("highlighted", "fg:ansicyan bold"),
        ("answer", "fg:ansigreen"),
        ("separator", "fg:ansibrightblack"),
        ("instruction", "fg:ansibrightblack"),
    ]
)

TITLE = "bold fg:ansicyan"
ART = "fg:ansicyan"
DIM = "fg:ansibrightblack"
NARRATOR = "italic fg:ansiyellow"
GOOD = "fg:ansigreen"
BAD = "bold fg:ansired"


class StoryChoice(TypedDict):
    label: str
    next: str
    requires: NotRequired[str]
    gives: NotRequired[str]


class Scene(TypedDict):
    text: str
    choices: list[StoryChoice]


class Story(TypedDict):
    start: str
    paths: dict[str, Scene]


class Action(Enum):
    STATUS = "Check status"
    JOURNAL = "Read journal"
    PROMISE = "Ask about the ending"
    QUIT = "Quit"


@dataclass
class GameState:
    player_name: str
    current_path: str
    turns: int = 0
    promises_heard: int = 0
    inventory: list[str] = field(default_factory=list)
    history: list[str] = field(default_factory=list)
    visits: dict[str, int] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.visits.setdefault(self.current_path, 1)

    @property
    def visits_here(self) -> int:
        return self.visits.get(self.current_path, 0)

    def can_take(self, choice: StoryChoice) -> bool:
        required = choice.get("requires")
        return required is None or required in self.inventory

    def take(self, choice: StoryChoice) -> str | None:
        """Follow a choice. Returns the item picked up along the way, if any."""
        item = choice.get("gives")
        picked_up = item if item and item not in self.inventory else None
        if picked_up:
            self.inventory.append(picked_up)

        previous = self.current_path
        self.current_path = choice["next"]
        self.turns += 1
        self.visits[self.current_path] = self.visits_here + 1
        self.history.append(
            f"Turn {self.turns}: {choice['label']} ({previous} -> {self.current_path})"
        )
        return picked_up


# ── Art ───────────────────────────────────────────────────────────────────────


def draw_room(interior: list[str]) -> str:
    """Wrap rows of text in a 3D box so the edges always line up."""
    rows = [row.ljust(ART_WIDTH)[:ART_WIDTH] for row in interior]
    edges = ["  |"] * (len(rows) - 2) + ["  /", " /"]
    lines = [
        " " * 5 + "_" * (ART_WIDTH + 1),
        " " * 4 + "/" + " " * ART_WIDTH + "/|",
        " " * 3 + "/" + " " * ART_WIDTH + "/ |",
        "  +" + "-" * ART_WIDTH + "+  |",
        *(f"  |{row}|{edge}" for row, edge in zip(rows, edges)),
        "  +" + "-" * ART_WIDTH + "+/",
    ]
    return "\n".join(lines)


ROOM_ART = draw_room(
    [
        "",
        "   +----------+      +----------+",
        "   |          |      |          |",
        "   |   LEFT   |      |  RIGHT   |",
        "   |   DOOR   |      |   DOOR   |",
        "   |        o |      | o        |",
        "   |          |      |          |",
    ]
)

WALL_ART = draw_room(
    ["", "", "", "A very plain wall".center(ART_WIDTH), "", "", ""]
)

# Paths without their own art fall back to the room.
PATH_ART: dict[str, str] = {"wall": WALL_ART}


# ── Output helpers ────────────────────────────────────────────────────────────


def say(text: str = "", style: str | None = None) -> None:
    questionary.print(text, style=style)


def text_width() -> int:
    return min(shutil.get_terminal_size((80, 24)).columns, MAX_TEXT_WIDTH)


def wrap(text: str) -> str:
    """Wrap to the terminal while keeping the story's own paragraph breaks."""
    width = text_width()
    return "\n".join(
        textwrap.fill(paragraph, width) if paragraph.strip() else ""
        for paragraph in text.splitlines()
    )


def rule(title: str) -> None:
    line = f"── {title} "
    say(line + "─" * max(text_width() - len(line), 2), style=TITLE)


def show_rows(rows: list[tuple[str, str]]) -> None:
    label_width = max(len(label) for label, _ in rows)
    for label, value in rows:
        say(f"  {label.ljust(label_width)}  {value}")


# ── Story loading ─────────────────────────────────────────────────────────────


def find_problems(story: Story) -> list[str]:
    paths = story.get("paths")
    if not isinstance(paths, dict) or not paths:
        return ['The story needs a non-empty "paths" object.']

    problems: list[str] = []
    start = story.get("start")
    if start not in paths:
        problems.append(f'Start path "{start}" is missing from paths.')

    for name, scene in paths.items():
        if "text" not in scene:
            problems.append(f'"{name}" has no text.')
        for index, choice in enumerate(scene.get("choices", []), start=1):
            where = f'"{name}" choice {index}'
            if "label" not in choice:
                problems.append(f"{where} has no label.")
            target = choice.get("next")
            if target not in paths:
                problems.append(f'{where} leads to unknown path "{target}".')

    return problems


def load_story(path: Path = STORY_PATH) -> Story:
    try:
        story: Story = json5.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise ValueError(f"Story file not found: {path}") from None
    except ValueError as error:
        raise ValueError(f"{path.name} is not valid JSON5: {error}") from error

    problems = find_problems(story)
    if problems:
        raise ValueError("\n".join(f"- {problem}" for problem in problems))

    for scene in story["paths"].values():
        scene.setdefault("choices", [])
    return story


# ── Screens ───────────────────────────────────────────────────────────────────


def show_scene(scene: Scene, state: GameState) -> None:
    say()
    rule(f"{state.current_path} · turn {state.turns}")
    say()
    say(wrap(scene["text"]))
    say()
    say(PATH_ART.get(state.current_path, ROOM_ART), style=ART)
    say()

    if state.visits_here > 1:
        say(f"You have been here {state.visits_here} times.", style=DIM)
    if state.turns > 0 and state.turns % REMINDER_EVERY == 0:
        say("The narrator reminds you that an ending has been promised.", style=NARRATOR)
    if not any(state.can_take(choice) for choice in scene["choices"]):
        say("There is nowhere to go from here.", style=DIM)


def show_status(state: GameState) -> None:
    say()
    rule("Status")
    show_rows(
        [
            ("Player", state.player_name),
            ("Turns taken", str(state.turns)),
            ("Current path", state.current_path),
            ("Times in this path", str(state.visits_here)),
            ("Promises of an ending", str(state.promises_heard)),
            ("Inventory", ", ".join(state.inventory) or "Nothing"),
        ]
    )
    say()


def show_journal(state: GameState) -> None:
    say()
    rule("Journal")
    if not state.history:
        say("  Nothing has happened yet.", style=DIM)
    for entry in state.history:
        say(f"  - {entry}")
    say()


def hear_promise(state: GameState) -> None:
    state.promises_heard += 1
    index = min(state.promises_heard, len(ENDING_PROMISES)) - 1
    say()
    say(wrap(ENDING_PROMISES[index]), style=NARRATOR)
    say()


# ── Game loop ─────────────────────────────────────────────────────────────────


def ask_name() -> str | None:
    """Returns None if the player backs out with Ctrl+C."""
    answer = questionary.text(
        "What should the narrator call you?",
        default=DEFAULT_NAME,
        style=PROMPT_STYLE,
    ).ask()
    if answer is None:
        return None
    return answer.strip() or DEFAULT_NAME


def ask_action(scene: Scene, state: GameState) -> StoryChoice | Action:
    moves = [
        Choice(title=choice["label"], value=choice)
        for choice in scene["choices"]
        if state.can_take(choice)
    ]
    extras = [Choice(title=action.value, value=action) for action in Action]
    divider = [Separator()] if moves else []

    answer = questionary.select(
        "What do you do?",
        choices=[*moves, *divider, *extras],
        style=PROMPT_STYLE,
    ).ask()
    return Action.QUIT if answer is None else answer


def play(story: Story, state: GameState) -> None:
    just_arrived = True

    while True:
        scene = story["paths"][state.current_path]
        if just_arrived:
            show_scene(scene, state)
            just_arrived = False

        selected = ask_action(scene, state)

        if selected is Action.QUIT:
            return
        if selected is Action.STATUS:
            show_status(state)
        elif selected is Action.JOURNAL:
            show_journal(state)
        elif selected is Action.PROMISE:
            hear_promise(state)
        else:
            item = state.take(selected)
            if item:
                say(f"+ Added to inventory: {item}", style=GOOD)
            just_arrived = True


def main() -> None:
    try:
        story = load_story()
    except ValueError as error:
        say("Could not load the story:", style=BAD)
        say(str(error))
        sys.exit(1)

    player_name = ask_name()
    if player_name is None:
        return

    state = GameState(player_name=player_name, current_path=story["start"])
    play(story, state)

    turns = "1 turn" if state.turns == 1 else f"{state.turns} turns"
    say()
    say(f"Goodbye, {state.player_name}. {turns} taken. The ending is still on its way.", style=NARRATOR)


if __name__ == "__main__":
    main()
