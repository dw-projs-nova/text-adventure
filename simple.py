from pathlib import Path

import questionary
import json5


story_path = Path("story-simple.jsonc")


def main():
    story = json5.loads(story_path.read_text(encoding="utf-8"))
    current_path = story["start"]

    while True:
        scene = story["paths"][current_path]
        print(f"\n{scene['text']}")

        choices = scene["choices"]
        if len(choices) == 0:
            break

        labels = []
        for choice in choices:
            labels.append(choice["label"])

        selected_label = questionary.select(
            "Choose an option:",
            choices=labels,
        ).ask()
        if selected_label is None:
            break

        for choice in choices:
            if choice["label"] == selected_label:
                current_path = choice["next"]
                break


if __name__ == "__main__":
    main()
