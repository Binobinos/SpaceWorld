from .spaceworld_cli import spaceworld


@spaceworld(
    name="spaceworld",
    docs="Spaceworld is a new generation Cli framework for convenient development of your teams written in "
         "Python 3.12+ with support for asynchronous commands",
    version="2.0.0",
)
def main(*, version: bool = False):
    print(main.help_text)
