
# First Steps

Let's start with the simplest example to get familiar with SpaceWorld.

## Your First Command

```python
from spaceworld import run


@run
def main():
    print("Hello World")
```

Copy this code into a file called `main.py` and run it:

```shell
$ python main.py
Hello World

$ python main.py --help
Usage: main [OPTIONS]
Activated modes: All
```

## Adding Your First Argument

Now let's make our command more useful by adding a name parameter:

```python
from spaceworld import run


@run
def hello(name: str):
    print(f"Hello {name}")
```

When we run this, something interesting happens:

```shell
$ python main.py hello
ERROR: Missing required argument: 'name'
```

SpaceWorld tells us exactly what's missing! Let's provide the name:

```shell
$ python main.py hello bino
Hello bino
```

Great! The command now greets us personally. But what if we want the greeting in uppercase? Let's add a flag for that.

## Working with Flags

Flags are special command-line arguments that start with `--`. Let's add an `upper` flag to control capitalization:

```python
from spaceworld import run


@run
def hello(name: str, upper: bool):
    if upper:
        print(f"HELLO {name.upper()}")
    else:
        print(f"Hello {name}")
```

Now let's test it:

```shell
$ python main.py hello bino
ERROR: Missing required argument: 'upper'

$ python main.py hello bino --upper
HELLO BINO
```

Perfect! The `--upper` flag converted our greeting to uppercase.

### Understanding Flags

There are two main types of flags in SpaceWorld:

1. **Boolean Flags** (like `--upper` and `--help`)
    - Their presence means `True`
    - Their absence means `False`
    - Format: `--flagname`

2. **Value Flags** (for passing specific values)
    - Format: `--name=value`
    - Example: `--count=5` or `--file=data.txt`

## Adding More Features

Let's expand our hello command with more options:

```python
from spaceworld import run


@run
def hello(name: str, age: int, upper: bool, informal: bool = False):
    greeting = "Hi" if informal else "Hello"
    message = f"{greeting} {name}! You are {age} years old!"
    print(message.upper() if upper else message)
```

Now we can use it in different ways:

```shell
$ python main.py hello bino 23 --upper
HELLO BINO! YOU ARE 23 YEARS OLD!

$ python main.py hello bino 23 --informal
Hi bino! You are 23 years old!

$ python main.py hello bino 23 --upper --informal
HI BINO! YOU ARE 23 YEARS OLD!
```

## Understanding Argument Order

One of SpaceWorld's nice features is that **flag order doesn't matter**. These all work the same:

```shell
$ python main.py hello bino 23 --upper --informal
$ python main.py hello bino 23 --informal --upper
$ python main.py hello --upper bino --informal 23
```

However, **positional argument order does matter**. Since SpaceWorld doesn't know which positional argument is which,
they're passed in the order you provide them:

```shell
# This works: name="bino", age=23
$ python main.py hello bino 23 --upper

# This fails: name="23", age="bino" (can't convert "bino" to integer)
$ python main.py hello 23 bino --upper
ERROR: Invalid argument for 'age': invalid literal for int() with base 10: 'bino'
```
