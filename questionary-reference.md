# Questionary Reference

Questionary provides interactive console prompts. The package is listed in `requirements.txt`.

## Text input

```python
import questionary

answer = questionary.text("What is your name?").ask()
```

`ask()` displays the prompt and returns the user's answer.

## Single-choice menu

```python
choice = questionary.select(
    "Choose a direction:",
    choices=["North", "South"],
).ask()
```

`select()` presents one choice at a time and supports arrow-key navigation. `ask()` returns the selected choice.

## Documentation

- [Questionary quickstart](https://questionary.readthedocs.io/en/stable/pages/quickstart.html)
- [Question types](https://questionary.readthedocs.io/en/stable/pages/types.html)
- [API reference](https://questionary.readthedocs.io/en/stable/pages/api_reference.html)
- [Installation](https://questionary.readthedocs.io/en/stable/pages/installation.html)
