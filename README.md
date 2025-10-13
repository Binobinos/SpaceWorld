# SpaceWorld
[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI version](https://img.shields.io/pypi/v/spaceworld?color=%2334D058&label=pypi%20package)](https://pypi.org/project/spaceworld)
[![PyPI Downloads](https://static.pepy.tech/badge/spaceworld)](https://pepy.tech/projects/spaceworld)

**Spaceworld is a new generation Cli framework for convenient development of your
teams written in Python 3.12+ with support for asynchronous commands**

Source Code: https://github.com/Binobinos/SpaceWorld

documentation: https://github.com/Binobinos/SpaceWorld/docs/README.md

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
from spaceworld import run


@run
def main():
    print("Hello World")

```

Copy that to a file main.py.

Test it:

```
$ python main.py

Hello World

$ python main.py --help

Usage: main [ARGS] [OPTIONS]  
None documentation

Options:
  --help - Displays the help on the command

```

# One Cli argument

This output for the function looks very simple.
Let's create a new function. hello, which displays a welcome message to the user

```python
from spaceworld import run


@run
def main(name: str):
    print(f"Hello {name}")

```

Now let's run this script and see what happens.

```shell
$ python spaceworld_.py 

ERROR: Missing required argument: 'name'
```

We see an error due to the absence of the name argument. Let's welcome bino

```shell
$ python spaceworld_.py bino

Hello bino
```
# Async command

Creating an asynchronous command

```python
import asyncio

from spaceworld import run


@run
async def main(second: int = 1):
    await asyncio.sleep(second)
    print(f"Hello in {second} second")

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

from spaceworld import run


@run
def main(
        age: Annotated[
          int,
          lambda x: x if x >= 18 else
          ValueError("The user must be over 18 years old")]):
  print(f"Hello {age} year old")

```

Copy that to a file main.py.

Test it:
```shell
$ python .\main.py 1

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

# 🆕 What's new in SpaceWorld 3.0?

- Improved framework structure

- Added support for TypedDict, byte, complex, bytearray, Unpack in *args, **kwargs

- Fixed errors with confirm and others

## License

This project is licensed under the terms of the MIT license.