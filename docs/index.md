# SpaceWorld

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI version](https://img.shields.io/pypi/v/spaceworld?color=%2334D058&label=pypi%20package)](https://pypi.org/project/spaceworld)
[![PyPI Downloads](https://static.pepy.tech/badge/spaceworld)](https://pepy.tech/projects/spaceworld)

**Spaceworld is a new generation Cli framework for convenient development of your
teams written in Python 3.12+ with support for asynchronous commands**

Source Code: https://github.com/Binobinos/SpaceWorld
documentation: https://binobinos.github.io/Spaceworld

The key features are:

- Highest speed: For high-load applications
    - Huge flexibility: The ability to customize handlers, commands, and modules
    - Code simplicity: With all the advantages, your code remains as simple as possible
    - Support for *args, **kwargs
    - Extended type annotations: Use new annotations like Annotated, Literal, Union, and others
    - Support for Validators and transformers in annotations

# Install Spaceworld

The first step is to install SpaceWorld.

First, make sure you create your virtual environment, activate it, and then install it, for example with:

```shell
pip install spaceworld
```

# Example

The simplest example

```python
import spaceworld


def main():
    print("Hello World")


if __name__ == '__main__':
    spaceworld.run(main)
```

Copy that to a file main.py.

Test it:

```
$ python main.py main

Hello World

$ python main.py main --help

Usage: main [ARGS] [OPTIONS]  
None documentation

Options:
  --help - Displays the help on the command

```

# One Cli argument

This output for the function looks very simple.
Let's create a new function. hello, which displays a welcome message to the user

```python
import spaceworld


def hello(name: str):
    print(f"Hello {name}")


if __name__ == '__main__':
    spaceworld.run(hello)
```

Now let's run this script and see what happens.

```shell
$ python spaceworld_.py hello

ERROR: Missing required argument: 'name'
```

We see an error due to the absence of the name argument. Let's welcome bino

```shell
$ python spaceworld_.py hello bino

Hello bino
```

# Async command

Creating an asynchronous command

```python
import asyncio

import spaceworld


async def sleep(second: int):
    await asyncio.sleep(second)
    print(f"Hello in {second} second")


if __name__ == '__main__':
    spaceworld.run(sleep)

```

Copy that to a file main.py.

Test it:

```shell
$ python .\main.py sleep 1

# After 1 second
Hello in 1 second

$ python .\main.py sleep

# After 1 second
Hello in 1 second

$ python .\main.py sleep 5

# After 5 second
Hello in 5 second
```

# The validation Command

Creating a validation Command

```python

from typing import Annotated

import spaceworld


def check(
        age: Annotated[
            int,
            lambda x: x if x >= 18 else
            ValueError("The user must be over 18 years old")]):
    print(f"Hello {age} year old")


if __name__ == '__main__':
    spaceworld.run(check)

```

Copy that to a file main.py.

Test it:

```shell
$ python .\main.py check 1

ERROR:Invalid argument for 'age':
Error in the Annotated validation for `1`: Arg: 1, Error: The user must be over 18 years old, <class 'spaceworld.exceptions.annotations_error.AnnotationsError'>      

$ python .\main.py check 15

ERROR:Invalid argument for 'age': 
Error in the Annotated validation for `15`: Arg: 15, Error: The user must be over 18 years old, <class 'spaceworld.exceptions.annotations_error.AnnotationsError'>

$ python .\main.py check 18

Hello 18 year old

$ python .\main.py check -1

ERROR:Invalid argument for 'age': 
Error in the Annotated validation for `-1`: Arg: -1, Error: The user must be over 18 years old, <class 'spaceworld.exceptions.annotations_error.AnnotationsError'>
```

---

# New features in v2.0.0

## The decorators' style

## Modules as a command

## Checking the number of positional and named arguments

Great!
As we can see, we entered the hello command with the bino argument and the script displayed greeting messages to him.

But what if we want to make a conclusion in big letters? Then let's add a flag.

## License

This project is licensed under the terms of the MIT license.