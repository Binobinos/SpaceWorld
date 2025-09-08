# First Steps

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

$ python main.py main bino 12 --help

Usage: main [OPTIONS]  
Activated modes: All

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
Great! 
As we can see, we entered the hello command with the bino argument and the script displayed greeting messages to him.

But what if we want to make a conclusion in big letters? Then let's add a flag.

# Adding the first flag

So we've come to an interesting section of the CLI - Flags! 
This is a vast topic, but let's change our existing feature first.

```python
import spaceworld


def hello(name: str, upper: bool):
    if upper:
        print(f"Hello {name}".upper())
    else:
        print(f"Hello {name}")


if __name__ == '__main__':
    spaceworld.run(hello)
```
For now, we've just added a new argument to the hello function called upper, which is of type bool. 
Let's call it up in the console and see what happens.

```shell
$ python spaceworld_.py hello bino

ERROR: Missing required argument: 'upper'
```
To begin with, we see that we have omitted the upper argument. 
To call it, we will need a special designation starting with a double dash.
```shell
$ python spaceworld_.py hello bino --upper

HELLO BINO
```
We see that by adding the --upper designation, the text has become written in capital letters.  
In order to understand why this worked, I need to explain what flags are and how they work.
Flags are an argument starting with a double dash. 
I can divide them into two types. Flags and flags with meaning. 
How do they differ? 
Let's take the already well-known --help flag and understand what it does. 
When we add it to a command in a command or module call, 
we usually see its description, usage examples, and other information. 
But it is not the description itself that is important to us, but rather the essence of the work. 
By specifying this flag, 
we tell the CLI: "Hey buddy, I need a hint on this command!". 
That is, the very fact of the presence of this argument indicates actions. 
I call this the Bool flag. 
Such flags indicate their meaning by their presence or absence. 
Let's go back to the example with --help. 
The very fact of its presence indicates a positive value (True) that you need to output the help, 
and its absence means False. 
If you understand the essence of bool flags, 
it is important to remember that such flags are indicated by a simple double dash at the beginning followed by the name of the argument. As in the already jammed case with --help, a double dash is a designation, and help is a name. Now, after explaining the flags for a long time, the second type will seem just as simple. I call them flags with a value. Flags with a value are the second type of flags. My framework uses the notation --name=value, where there is a double dash first, the argument name, the equal sign, and the value after. But it's worth noting that other frameworks have a different notation without an equal sign. The point here is simple. There is a name and a meaning. Nothing else.
# The order of the arguments
In SpaceWorld, the order of flags and positional arguments is not important. 
I'll give you an example, but first we'll update the code and add more arguments.

```python
import spaceworld


def hello(name: str, age: int, upper: bool, hi: bool = False):
    string = f"{"Hi" if hi else "Hello"} {name}! You are {age} years old!"
    print(string.upper() if upper else string)


if __name__ == '__main__':
    spaceworld.run(hello)
```
I added two new arguments. These are age and the hi flag, which is set to False by default.
Let's call this function:
```shell
$ python spaceworld_.py hello bino 15 --upper

HELLO BINO! YOU ARE 15 YEARS OLD!

$ python spaceworld_.py hello bino 15 --upper --hi

HI BINO! YOU ARE 15 YEARS OLD!

$ python spaceworld_.py hello bino 15 --hi --upper

HI BINO! YOU ARE 15 YEARS OLD

$ python spaceworld_.py hello --hi --upper bino 15

HI BINO! YOU ARE 15 YEARS OLD

$ python spaceworld_.py hello --hi bino --upper 15

HI BINO! YOU ARE 15 YEARS OLD

$ python spaceworld_.py hello bino --hi --upper 15

HI BINO! YOU ARE 15 YEARS OLD
```
As we can see, the order of the flags and arguments does not affect the result. But what if we swap bino and 15 places?
```shell
$ python spaceworld_.py hello 15 bino --hi --upper

ERROR: Invalid argument for 'age': invalid literal for int() with base 10: 'bino'
```
As we can see, after changing the order of the positional arguments, an error occurred, 
since the age argument is specified as int, and we are feeding the string bino.
---

From this, we can conclude that the order of the arguments and flags among themselves is not important, unlike the order of the positional arguments, since their incorrect order may affect the logic of the function.
---
In this section, I have shown you all the basic features for creating simple CLI applications. So let's move on.
