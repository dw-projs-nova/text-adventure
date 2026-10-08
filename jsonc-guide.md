# Reading the Story File

`story.jsonc` contains JSON data with comments. Python's built-in `json` module does not accept comments, so this project uses `json5` to read it.

Install project packages from the workspace folder:

```powershell
pip install -r requirements.txt
```

## Load the file

```python
from pathlib import Path

import json5

story = json5.loads(Path("story.jsonc").read_text(encoding="utf-8"))
```

The loaded data is made of ordinary Python dictionaries and lists. The `start` field gives the first path ID. Use it to look up a scene in `paths`:

```python
current_path = story["start"]
scene = story["paths"][current_path]
print(scene["text"])
```

## Follow a choice

Each scene's `choices` list contains a display label and the ID of the next path. Questionary can show those labels as a menu:

```python
import questionary

choices = scene["choices"]
selected_label = questionary.select(
    "What do you do?",
    choices=[choice["label"] for choice in choices],
).ask()

next_path = next(
    choice["next"] for choice in choices
    if choice["label"] == selected_label
)
```

To display the next scene, look up `story["paths"][next_path]`. An empty `choices` list means that path is an ending.

See [Questionary's select documentation](https://questionary.readthedocs.io/en/stable/pages/types.html#select) for menu options.

## Start with the first scene

The `start` value in `story.jsonc` is `"arrival"`. That is a key in the `paths` dictionary, so `story["paths"]["arrival"]` gets the opening scene. To see it run, put this inside `main()` after loading `story`:

```python
current_path = story["start"]
scene = story["paths"][current_path]

print(scene["text"])
selected_label = questionary.select(
    "What do you do?",
    choices=[choice["label"] for choice in scene["choices"]],
).ask()

current_path = next(
    choice["next"] for choice in scene["choices"]
    if choice["label"] == selected_label
)
print("Next path:", current_path)
```

Run the file from the project folder with:

```powershell
python main.py
```

The first printed text should be the lighthouse arrival. Choosing an option sets `current_path` to its `next` ID, such as `"hall"` or `"shore"`. That ID can then be used to get the next scene with `story["paths"][current_path]`. This example only handles one choice; it does not include a loop for continuing through the whole story.
