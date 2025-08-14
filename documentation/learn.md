# Learn

Learn how to use SpaceWorld from this step-by-step user guide.

You can learn all the features of SpaceWorld in this guide for creating simple and complex CLI applications. 
Let's go on a space trip using this framework!

# Python type

First of all, if you are not familiar with Python annotations, let's study them.

```python
def hello(name: str, upper: bool = False) -> None:
    string = f"Hello {name}"
    
    print(string.upper() if upper else string)
```
This example shows a few things:
- name is of type str(string) and is a mandatory argument.
- upper is a bool (boolean value) and is optional, since there is a default value of False.

This annotation affects the resulting function value and validation in SpaceWorld.


# Run the Code
All the code blocks can be copied and used directly (they are tested Python files).

To run any of the examples, copy the code to a file main.py, and run it:

```shell
python app.py
```