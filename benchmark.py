#!/usr/bin/env python3
"""
SpaceWorld CLI Framework Benchmark Tool
"""

import argparse
import cProfile
import json
import os
import platform
import pstats
import statistics
import sys
import timeit
import traceback
import tracemalloc
from contextlib import contextmanager
from datetime import datetime
from importlib.metadata import version
from typing import Dict, List, Callable, Any, Optional, Set, Annotated

import click
import cloup
import fire
import typer
from rich.box import ROUNDED
from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, BarColumn, TextColumn
from rich.rule import Rule
from rich.table import Table
from rich.text import Text

import spaceworld
from spaceworld import run

DEFAULT_RUNS = 1000
DEFAULT_WARMUP = 5
DEFAULT_OUTPUT = "benchmark_results.json"
LIBRARY_COLORS = {
    "click": "yellow",
    "typer": "magenta",
    "spaceworld": "cyan",
    "testfunc": "green",
    "argparse": "blue",
    "fire": "red",
    "cloup": "white",
}

console = Console()


class TestScenario:
    def __init__(
            self, name: str, command: str, description: str = "", complexity: str = "simple"
    ):
        self.name = name
        self.command = command
        self.description = description
        self.complexity = complexity


DEFAULT_SCENARIOS = [
    TestScenario(
        name="simple_command",
        command="hello 10",
        description="A simple command with one argument",
        complexity="simple",
    ),
    TestScenario(
        name="subcommand",
        command="subcmd 10 --verbose",
        description="A command with a subcommand and a flag",
        complexity="medium",
    ),
    TestScenario(
        name="multiple_options",
        command="validate 50 --min 0 --max 100 --name test",
        description="Command with multiple options and validation",
        complexity="medium",
    ),
    TestScenario(
        name="complex_nesting",
        command="group subgroup command --flag1 --option value --list item1,item2,item3",
        description="Deeply nested subcommands with multiple flags and lists",
        complexity="complex",
    ),
    TestScenario(
        name="file_processing",
        command="process --input large_file.txt --output result.txt --encoding utf-8 --overwrite",
        description="File processing with multiple string options and flags",
        complexity="medium",
    ),
    TestScenario(
        name="math_operations",
        command="calculate 15 --operation multiply --factor 3.14 --precision high --round 2",
        description="Mathematical operations with numeric options",
        complexity="medium",
    ),
    TestScenario(
        name="api_client",
        command="api get /users --headers auth_token:xyz --params page:1,limit:50 --timeout 10 --retry 2",
        description="API client simulation with complex parameters",
        complexity="complex",
    ),
    TestScenario(
        name="config_management",
        command="config set database.host localhost --type string --env production --global_ --force",
        description="Configuration management with nested options",
        complexity="complex",
    ),
]


class BenchmarkResult:
    def __init__(self):
        self.times: List[float] = []
        self.memory_usage: List[int] = []
        self.profile_data: Optional[Dict] = None

    @property
    def avg_time(self) -> float:
        return statistics.mean(self.times) if self.times else 0

    @property
    def avg_memory(self) -> float:
        return statistics.mean(self.memory_usage) if self.memory_usage else 0

    @property
    def peak_memory(self) -> float:
        return max(self.memory_usage) if self.memory_usage else 0


class BenchmarkLibrary:
    def __init__(
            self,
            name: str,
            setup_func: Callable,
            execute_func: Callable,
            enabled: bool = True,
    ):
        self.name = name
        self.setup_func = setup_func
        self.execute_func = execute_func
        self.enabled = enabled
        self.color = LIBRARY_COLORS.get(name, "white")
        self.version = self._get_version()
        self.results: Dict[str, BenchmarkResult] = {}

    def _get_version(self) -> str:
        if self.name == "testfunc":
            return "1.0"
        try:
            return version(self.name)
        except:
            return "unknown"

    def run_test(
            self, scenario: TestScenario, runs: int, warmup: int, measure_memory: bool
    ) -> BenchmarkResult:
        result = BenchmarkResult()
        env = self.setup_func()
        timer = timeit.Timer(lambda: self.execute_func(env, scenario.command))
        result.times = timer.repeat(repeat=runs, number=1)

        if measure_memory:
            for _ in range(runs):
                tracemalloc.start()
                self.execute_func(env, scenario.command)
                _, peak = tracemalloc.get_traced_memory()
                tracemalloc.stop()
                result.memory_usage.append(peak)

        self.results[scenario.name] = result
        return result

    def run_profiling(self, scenario: TestScenario, runs: int = 1) -> Dict[str, Any]:
        env = self.setup_func()
        profiler = cProfile.Profile(timeunit=False, subcalls=False)

        profiler.enable()
        self.execute_func(env, scenario.command)
        profiler.disable()

        stats = pstats.Stats(profiler)
        stats.sort_stats(pstats.SortKey.TIME)
        top_functions = []

        # Собираем и фильтруем результаты
        for func, (cc, nc, tt, ct, callers) in stats.stats.items():
            file, line, func_name = func
            normalized_time = ct / runs

            top_functions.append(
                {
                    "function": func_name,
                    "location": f"{os.path.basename(file)}:{line}",
                    "time": normalized_time,
                    "time_str": format_time(normalized_time),
                    "calls": nc,  # Добавляем количество вызовов
                }
            )

        sorted_functions = sorted(top_functions, key=lambda x: -x["time"])

        total_time = sum(f["time"] for f in sorted_functions)
        total_calls = sum(f["calls"] for f in sorted_functions)

        return {
            "top_functions": sorted_functions,
            "total_time": total_time,
            "total_time_str": format_time(total_time),
            "total_calls": total_calls,
        }


class BenchmarkRunner:
    def __init__(self):
        self.libraries: Dict[str, BenchmarkLibrary] = {}
        self.scenarios: List[TestScenario] = DEFAULT_SCENARIOS
        self.results: Dict[str, Dict[str, BenchmarkResult]] = {}
        self.config = {
            "runs": DEFAULT_RUNS,
            "warmup": DEFAULT_WARMUP,
            "output": DEFAULT_OUTPUT,
            "memory": True,
            "profile": False,
        }

    def add_library(self, library: BenchmarkLibrary) -> None:
        self.libraries[library.name] = library

    def add_scenario(self, scenario: TestScenario) -> None:
        self.scenarios.append(scenario)

    def run_benchmarks(self) -> None:
        with Progress(
                TextColumn("[bold blue]{task.description}"),
                BarColumn(bar_width=50),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                console=console,
        ) as progress:
            total = len(self.libraries) * len(self.scenarios)
            task = progress.add_task("Running benchmarks", total=total)

            for scenario in self.scenarios:
                for lib_name, library in self.libraries.items():
                    if not library.enabled:
                        continue

                    progress.update(
                        task,
                        description=f"[{library.color}]Testing {lib_name} - {scenario.name}",
                    )

                    try:
                        result = library.run_test(
                            scenario,
                            self.config["runs"],
                            self.config["warmup"],
                            self.config["memory"],
                        )

                        if self.config["profile"]:
                            profile_data = library.run_profiling(scenario)
                            result.profile_data = profile_data

                        self.results.setdefault(scenario.name, {})[lib_name] = result

                    except Exception as e:
                        console.print(f"[red]Error testing {lib_name}: {e}")
                        traceback.print_exc()

                    progress.update(task, advance=1)

    def print_results(self) -> None:
        console.print()
        console.rule(
            "[bold magenta]📊 Comprehensive Benchmark Results[/]", style="bold magenta"
        )

        self._print_system_info()

        self._print_summary_table()

        for scenario in self.scenarios:
            if scenario.name not in self.results:
                continue

            console.print()
            console.rule(
                f"[bold]Scenario: [cyan]{scenario.name}[/] - {scenario.description}",
                style="bold blue",
            )

            self._print_time_table(scenario)

            if self.config["memory"]:
                self._print_memory_table(scenario)

            if self.config["profile"]:
                self._print_profiling_results(scenario)

    def _print_system_info(self) -> None:
        """Выводит информацию о системе и версиях библиотек"""
        sys_info = Table.grid(padding=(0, 2))
        sys_info.add_column(style="bold")
        sys_info.add_column()

        sys_info.add_row("🖥️ System:", f"{platform.system()} {platform.release()}")
        sys_info.add_row("🐍 Python:", sys.version.split()[0])
        sys_info.add_row("📅 Date:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        sys_info.add_row("🏃 Runs:", str(self.config["runs"]))
        sys_info.add_row("🔥 Warmup:", str(self.config["warmup"]))

        console.print(
            Panel.fit(sys_info, title="⚙️ System Information", border_style="yellow")
        )

        # Версии библиотек
        libs_table = Table(
            title="📚 Tested Libraries",
            box=ROUNDED,
            show_header=True,
            header_style="bold cyan",
        )
        libs_table.add_column("Library")
        libs_table.add_column("Version")
        libs_table.add_column("Status")

        for lib in self.libraries.values():
            status = "[green]✓" if lib.enabled else "[red]✗"
            libs_table.add_row(f"[{lib.color}]{lib.name}[/]", lib.version, status)

        console.print()
        console.print(libs_table)

    def _print_summary_table(self) -> None:
        summary_table = Table(
            title="🏆 Performance Summary (All Scenarios)",
            box=ROUNDED,
            show_header=True,
            header_style="bold magenta",
        )

        summary_table.add_column("Library", style="bold", width=12)
        summary_table.add_column("Time (μs)", justify="right", width=12)
        summary_table.add_column("Memory", justify="right", width=12)
        summary_table.add_column("Time Factor", justify="right", width=12)
        summary_table.add_column("Efficiency", justify="right", width=12)
        summary_table.add_column("Performance", justify="left")

        lib_results = {}
        for lib_name in self.libraries:
            if not self.libraries[lib_name].enabled:
                continue

            total_time = 0
            total_memory = 0
            count = 0

            for scenario in self.scenarios:
                if (
                        scenario.name in self.results
                        and lib_name in self.results[scenario.name]
                ):
                    result = self.results[scenario.name][lib_name]
                    total_time += result.avg_time
                    total_memory += result.avg_memory
                    count += 1

            if count > 0:
                lib_results[lib_name] = {
                    "avg_time": total_time / count,
                    "avg_memory": total_memory / count,
                }

        best_time = min(result["avg_time"] for result in lib_results.values())
        best_memory = min(result["avg_memory"] for result in lib_results.values())

        for lib_name, result in sorted(
                lib_results.items(), key=lambda x: x[1]["avg_time"]
        ):
            lib = self.libraries[lib_name]

            time_factor = result["avg_time"] / best_time
            memory_factor = result["avg_memory"] / best_memory if best_memory > 0 else 1
            efficiency = (1 / time_factor + 1 / memory_factor) / 2

            perf_indicator = self._generate_performance_indicator(time_factor)

            summary_table.add_row(
                f"[bold {lib.color}]{lib_name}[/]",
                f"[cyan]{result['avg_time'] * 1e6:.2f}[/]",
                f"[green]{format_memory(result['avg_memory'])}[/]",
                f"[yellow]{time_factor:.1f}x[/]",
                f"[bold]{efficiency:.1%}[/]",
                perf_indicator,
            )

        console.print()
        console.print(summary_table)
        console.print(
            "\n[dim]Time Factor: Relative to fastest library (lower is better)"
        )
        console.print(
            "[dim]Efficiency: Combined metric of speed and memory (higher is better)"
        )

    def _print_time_table(self, scenario: TestScenario) -> None:
        """Выводит таблицу времени с улучшенным форматированием"""
        time_table = Table(
            title="⏱️ Execution Time",
            box=ROUNDED,
            show_header=True,
            header_style="bold green",
        )

        time_table.add_column("Library", style="bold", width=12)
        time_table.add_column("Avg (μs)", justify="right", width=10)
        time_table.add_column("Min (μs)", justify="right", width=10)
        time_table.add_column("Max (μs)", justify="right", width=10)
        time_table.add_column("Std Dev", justify="right", width=10)
        time_table.add_column("Factor", justify="right", width=8)
        time_table.add_column("Performance", justify="left")

        scenario_results = self.results[scenario.name]
        if not scenario_results:
            return

        fastest_time = min(result.avg_time for result in scenario_results.values())

        for lib_name, result in sorted(
                scenario_results.items(), key=lambda x: x[1].avg_time
        ):
            lib = self.libraries[lib_name]

            relative = result.avg_time / fastest_time if fastest_time > 0 else 1
            performance_bar = self._generate_performance_bar(relative)

            if len(result.times) > 1:
                std_dev = statistics.stdev(result.times)
                std_dev_str = f"{std_dev * 1e6:.2f} μs"
            else:
                std_dev_str = "N/A"

            time_table.add_row(
                f"[{lib.color}]{lib_name}[/]",
                f"{result.avg_time * 1e6:.2f}",
                f"{min(result.times) * 1e6:.2f}",
                f"{max(result.times) * 1e6:.2f}",
                std_dev_str,
                f"{relative:.1f}x",
                performance_bar,
            )

        console.print()
        console.print(time_table)

    def _print_memory_table(self, scenario: TestScenario) -> None:
        if not self.config["memory"]:
            return

        mem_table = Table(
            title="🧠 Memory Usage",
            box=ROUNDED,
            show_header=True,
            header_style="bold blue",
        )

        mem_table.add_column("Library", style="bold", width=12)
        mem_table.add_column("Avg", justify="right", width=12)
        mem_table.add_column("Peak", justify="right", width=12)
        mem_table.add_column("Factor", justify="right", width=8)
        mem_table.add_column("Efficiency", justify="left")

        scenario_results = self.results[scenario.name]
        if not scenario_results:
            return

        min_memory = min(result.avg_memory for result in scenario_results.values())

        for lib_name, result in sorted(
                scenario_results.items(), key=lambda x: x[1].avg_memory
        ):
            lib = self.libraries[lib_name]

            relative = result.avg_memory / min_memory if min_memory > 0 else 1
            efficiency_bar = self._generate_efficiency_bar(relative)

            mem_table.add_row(
                f"[{lib.color}]{lib_name}[/]",
                format_memory(result.avg_memory),
                format_memory(result.peak_memory),
                f"{relative:.1f}x",
                efficiency_bar,
            )

        console.print()
        console.print(mem_table)

    def _generate_performance_indicator(self, factor: float) -> str:
        if factor <= 1.5:
            return "[bold green]★★★★★[/] Exceptional"
        elif factor <= 3:
            return "[green]★★★★☆[/] Excellent"
        elif factor <= 10:
            return "[yellow]★★★☆☆[/] Good"
        elif factor <= 50:
            return "[orange]★★☆☆☆[/] Fair"
        else:
            return "[red]★☆☆☆☆[/] Poor"

    def _generate_performance_bar(self, relative: float) -> str:
        if relative <= 1.2:
            return "[green]▰▰▰▰▰▰▰▰▰▰[/]"
        elif relative <= 2:
            return "[green]▰▰▰▰▰▰▰▰▱▱[/]"
        elif relative <= 5:
            return "[yellow]▰▰▰▰▰▰▱▱▱▱[/]"
        elif relative <= 20:
            return "[yellow]▰▰▰▰▱▱▱▱▱▱[/]"
        elif relative <= 100:
            return "[orange]▰▰▱▱▱▱▱▱▱▱[/]"
        else:
            return "[red]▰▱▱▱▱▱▱▱▱▱[/]"

    def _generate_efficiency_bar(self, relative: float) -> str:
        if relative <= 1.2:
            return "[green]▰▰▰▰▰▰▰▰▰▰[/]"
        elif relative <= 2:
            return "[green]▰▰▰▰▰▰▰▰▱▱[/]"
        elif relative <= 5:
            return "[yellow]▰▰▰▰▰▰▱▱▱▱[/]"
        elif relative <= 10:
            return "[yellow]▰▰▰▰▱▱▱▱▱▱[/]"
        elif relative <= 20:
            return "[orange]▰▰▱▱▱▱▱▱▱▱[/]"
        else:
            return "[red]▰▱▱▱▱▱▱▱▱▱[/]"

    def _print_profiling_results(self, scenario: TestScenario) -> None:
        if not self.config["profile"]:
            return

        console.print()
        console.rule("[bold magenta]📊 Profiling Results[/]", style="bold magenta")

        for lib_name, result in self.results[scenario.name].items():
            if not result.profile_data:
                continue

            lib = self.libraries[lib_name]

            profile_table = Table(
                title=f"[{lib.color}]{lib_name}[/] - Top Functions",
                box=ROUNDED,
                show_header=True,
                header_style=f"bold {lib.color}",
            )

            profile_table.add_column("Function", style="bold")
            profile_table.add_column("Location", style="dim")
            profile_table.add_column("Time", justify="right")

            for func in result.profile_data["top_functions"]:
                profile_table.add_row(
                    func["function"], func["location"], func["time_str"]
                )

            console.print()
            console.print(profile_table)

    def save_results(self, filename: str = None) -> None:
        filename = filename or self.config["output"]
        results = {
            "config": self.config,
            "scenarios": [s.__dict__ for s in self.scenarios],
            "results": {
                scenario: {
                    lib: {"times": res.times, "memory_usage": res.memory_usage}
                    for lib, res in scenario_res.items()
                }
                for scenario, scenario_res in self.results.items()
            },
            "system": {
                "platform": platform.platform(),
                "python": sys.version,
                "timestamp": datetime.now().isoformat(),
            },
        }

        with open(filename, "w") as f:
            json.dump(results, f, indent=2)

        console.print(f"\n[green]✓ Results saved to {filename}")

    def load_results(self, filename: str) -> None:
        with open(filename, "r") as f:
            data = json.load(f)
            self.config = data["config"]
            self.scenarios = [TestScenario(**s) for s in data["scenarios"]]
            self.results = {
                scenario: {lib: BenchmarkResult() for lib in lib_res.keys()}
                for scenario, lib_res in data["results"].items()
            }

        console.print(f"\n[green]✓ Results loaded from {filename}")


def format_time(seconds: float) -> str:
    if seconds < 1e-6:
        return f"{seconds * 1e9:.2f} ns"
    elif seconds < 1e-3:
        return f"{seconds * 1e6:.2f} μs"
    elif seconds < 1:
        return f"{seconds * 1e3:.2f} ms"
    return f"{seconds:.4f} s"


def format_memory(bytes_val: int) -> str:
    if bytes_val < 1024:
        return f"{bytes_val} B"
    elif bytes_val < 1024 ** 2:
        return f"{bytes_val / 1024:.2f} KB"
    elif bytes_val < 1024 ** 3:
        return f"{bytes_val / (1024 ** 2):.2f} MB"
    return f"{bytes_val / (1024 ** 3):.2f} GB"


def print_welcome(scenarios: List[TestScenario], libraries: Set[str]) -> None:
    console.clear()
    console.rule("[bold blue]🚀 CLI Framework Benchmark Tool[/]", style="bold blue")

    # ASCII арт
    rocket = Text(
        """
          /\\
         /  \\
        /____\\
        |    |
        |SPW |
       /|____|\\
      /_|____|_\\
        |    |
        |    |
        |    |
       /      \\
      /        \\
    """,
        style="cyan",
    )

    scenarios_text = "\n".join(
        f"• [bold]{s.name}[/]: {s.description} ([{get_complexity_color(s.complexity)}]{s.complexity}[/])"
        for s in scenarios
    )

    libs_text = " ".join(
        f"• [{LIBRARY_COLORS.get(lib, 'white')}]{lib}[/]" for lib in libraries
    )

    info = Panel.fit(
        f"[b]Welcome to SpaceWorld Benchmark![/b]\n\n"
        f"[b]Test Scenarios:[/b]\n{scenarios_text}\n\n"
        f"[b]Libraries:[/b]\n{libs_text}\n\n"
        f"[b]Metrics:[/b]\n"
        "• ⏱️ Execution time\n"
        "• 🧠 Memory usage\n"
        "• 🔍 Function profiling",
        title="[green]Test Configuration[/]",
        border_style="green",
    )

    console.print(Columns([rocket, info], padding=2))
    console.print(Rule(style="blue"))


def get_complexity_color(complexity: str) -> str:
    return {"simple": "green", "medium": "yellow", "complex": "red"}.get(
        complexity, "white"
    )


def setup_click() -> Any:
    @click.group()
    def cli():
        pass

    @cli.command()
    @click.argument("num", type=int)
    def hello(num):
        pass

    @cli.command()
    @click.argument("num", type=int)
    @click.option("--verbose", is_flag=True)
    def subcmd(num, verbose):
        pass

    @cli.command()
    @click.argument("value", type=int)
    @click.option("--min", type=int, default=0)
    @click.option("--max", type=int, default=100)
    @click.option("--name", type=str)
    def validate(value, min, max, name):
        pass

    # Новые команды для дополнительных сценариев
    @cli.group()
    def group():
        pass

    @group.group()
    def subgroup():
        pass

    @subgroup.command()
    @click.option("--flag1", is_flag=True)
    @click.option("--option", type=str)
    @click.option("--list", type=str)
    def command(flag1, option, list):
        pass

    @cli.command()
    @click.option("--input", type=str)
    @click.option("--output", type=str)
    @click.option("--encoding", type=str)
    @click.option("--overwrite", is_flag=True)
    def process(input, output, encoding, overwrite):
        pass

    @cli.command()
    @click.argument("number", type=float)
    @click.option("--operation", type=str)
    @click.option("--factor", type=float)
    @click.option("--precision", type=str)
    @click.option("--round", type=int)
    def calculate(number, operation, factor, precision, round):
        pass

    @cli.command()
    @click.argument("email", type=str)
    @click.option("--domain-check", is_flag=True)
    @click.option("--format-strict", is_flag=True)
    @click.option("--timeout", type=int)
    @click.option("--retry", type=int)
    def check(email, domain_check, format_strict, timeout, retry):
        pass

    @cli.group()
    def api():
        pass

    @api.command()
    @click.argument("endpoint", type=str)
    @click.option("--headers", type=str)
    @click.option("--params", type=str)
    @click.option("--timeout", type=int)
    @click.option("--retry", type=int)
    def get(endpoint, headers, params, timeout, retry):
        pass

    @cli.group()
    def config():
        pass

    @config.command()
    @click.argument("key", type=str)
    @click.argument("value", type=str)
    @click.option("--type", type=str)
    @click.option("--env", type=str)
    @click.option("--global_", is_flag=True)
    @click.option("--force", is_flag=True)
    def set(key, value, type, env, global_, force):
        pass

    return cli


def setup_typer() -> Any:
    app = typer.Typer()

    @app.command()
    def hello(num: int):
        pass

    @app.command()
    def subcmd(num: int, verbose: bool = False):
        pass

    @app.command()
    def validate(
            value: int,
            min_val: int = typer.Option(0, "--min"),
            max_val: int = typer.Option(100, "--max"),
            name: str = typer.Option("", "--name"),
    ):
        pass

    # Новые команды для дополнительных сценариев
    group_app = typer.Typer()
    subgroup_app = typer.Typer()
    app.add_typer(group_app, name="group")
    group_app.add_typer(subgroup_app, name="subgroup")

    @subgroup_app.command()
    def command(flag1: bool = False, option: str = "", list: str = ""):
        pass

    @app.command()
    def process(
            input: str = typer.Option(..., "--input"),
            output: str = typer.Option(..., "--output"),
            encoding: str = typer.Option("utf-8", "--encoding"),
            overwrite: bool = False,
    ):
        pass

    @app.command()
    def calculate(
            number: float,
            operation: str = typer.Option(..., "--operation"),
            factor: float = typer.Option(1.0, "--factor"),
            precision: str = typer.Option("medium", "--precision"),
            round: int = typer.Option(0, "--round"),
    ):
        pass

    @app.command()
    def check(
            email: str,
            domain_check: bool = False,
            format_strict: bool = False,
            timeout: int = typer.Option(30, "--timeout"),
            retry: int = typer.Option(1, "--retry"),
    ):
        pass

    api_app = typer.Typer()
    app.add_typer(api_app, name="api")

    @api_app.command()
    def get(
            endpoint: str,
            headers: str = typer.Option("", "--headers"),
            params: str = typer.Option("", "--params"),
            timeout: int = typer.Option(30, "--timeout"),
            retry: int = typer.Option(1, "--retry"),
    ):
        pass

    config_app = typer.Typer()
    app.add_typer(config_app, name="config")

    @config_app.command()
    def set(
            key: str,
            value: str,
            type: str = typer.Option("string", "--type"),
            env: str = typer.Option("development", "--env"),
            global_: bool = typer.Option(False, "--global_"),
            force: bool = False,
    ):
        pass

    return app


def setup_spaceworld() -> Any:
    @spaceworld.spaceworld()
    def app():
        pass

    @app.module()
    def api():
        pass

    @app.module()
    def config():
        pass

    @app.module()
    def group():
        pass

    @group.module()
    def subgroup():
        pass

    @app.command()
    def hello(num: int):
        pass

    @app.command()
    def subcmd(num: int, verbose: bool = False):
        pass

    @app.command()
    def validate(value: int, min: int = 0, max: int = 100, name: str = ""):
        pass

    @subgroup.command()
    def command(flag1: bool = False, option: str = "", list: str = ""):
        pass

    @app.command()
    def process(
            input: str = "",
            output: str = "",
            encoding: str = "utf-8",
            overwrite: bool = False,
    ):
        pass

    @app.command()
    def calculate(
            number: float,
            operation: str = "",
            factor: float = 1.0,
            precision: str = "medium",
            round: int = 0,
    ):
        pass

    @app.command()
    def check(
            email: str,
            domain_check: bool = False,
            format_strict: bool = False,
            timeout: int = 30,
            retry: int = 1,
    ):
        pass

    @api.command()
    def get(
            endpoint: str,
            headers: str = "",
            params: str = "",
            timeout: int = 30,
            retry: int = 1,
    ):
        pass

    @config.command()
    def set(
            key: str,
            value: str,
            type: str = "string",
            env: str = "development",
            global_: bool = False,
            force: bool = False,
    ):
        pass

    return app


def setup_argparse() -> Any:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")

    # Базовые команды
    hello_parser = subparsers.add_parser("hello")
    hello_parser.add_argument("num", type=int)

    subcmd_parser = subparsers.add_parser("subcmd")
    subcmd_parser.add_argument("num", type=int)
    subcmd_parser.add_argument("--verbose", action="store_true")

    validate_parser = subparsers.add_parser("validate")
    validate_parser.add_argument("value", type=int)
    validate_parser.add_argument("--min", type=int, default=0)
    validate_parser.add_argument("--max", type=int, default=100)
    validate_parser.add_argument("--name", type=str, default="")

    # Новые команды для дополнительных сценариев
    group_parser = subparsers.add_parser("group")
    group_subparsers = group_parser.add_subparsers(dest="subcommand")

    subgroup_parser = group_subparsers.add_parser("subgroup")
    subgroup_subparsers = subgroup_parser.add_subparsers(dest="subsubcommand")

    command_parser = subgroup_subparsers.add_parser("command")
    command_parser.add_argument("--flag1", action="store_true")
    command_parser.add_argument("--option", type=str)
    command_parser.add_argument("--list", type=str)

    process_parser = subparsers.add_parser("process")
    process_parser.add_argument("--input", type=str, required=True)
    process_parser.add_argument("--output", type=str, required=True)
    process_parser.add_argument("--encoding", type=str, default="utf-8")
    process_parser.add_argument("--overwrite", action="store_true")

    calculate_parser = subparsers.add_parser("calculate")
    calculate_parser.add_argument("number", type=float)
    calculate_parser.add_argument("--operation", type=str, required=True)
    calculate_parser.add_argument("--factor", type=float, default=1.0)
    calculate_parser.add_argument("--precision", type=str, default="medium")
    calculate_parser.add_argument("--round", type=int, default=0)

    check_parser = subparsers.add_parser("check")
    check_parser.add_argument("email", type=str)
    check_parser.add_argument("--domain-check", action="store_true")
    check_parser.add_argument("--format-strict", action="store_true")
    check_parser.add_argument("--timeout", type=int, default=30)
    check_parser.add_argument("--retry", type=int, default=1)

    api_parser = subparsers.add_parser("api")
    api_subparsers = api_parser.add_subparsers(dest="apicommand")

    api_get_parser = api_subparsers.add_parser("get")
    api_get_parser.add_argument("endpoint", type=str)
    api_get_parser.add_argument("--headers", type=str, default="")
    api_get_parser.add_argument("--params", type=str, default="")
    api_get_parser.add_argument("--timeout", type=int, default=30)
    api_get_parser.add_argument("--retry", type=int, default=1)

    config_parser = subparsers.add_parser("config")
    config_subparsers = config_parser.add_subparsers(dest="configcommand")

    config_set_parser = config_subparsers.add_parser("set")
    config_set_parser.add_argument("key", type=str)
    config_set_parser.add_argument("value", type=str)
    config_set_parser.add_argument("--type", type=str, default="string")
    config_set_parser.add_argument("--env", type=str, default="development")
    config_set_parser.add_argument("--global_", action="store_true")
    config_set_parser.add_argument("--force", action="store_true")

    return parser


def setup_fire() -> Any:
    class FireApp:
        def hello(self, num: int):
            pass

        def subcmd(self, num: int, verbose: bool = False):
            pass

        def validate(self, value: int, min: int = 0, max: int = 100, name: str = ""):
            pass

        # Новые команды для дополнительных сценариев
        def group(self):
            return self

        def subgroup(self):
            return self

        def command(self, flag1: bool = False, option: str = "", list: str = ""):
            pass

        def process(
                self,
                input: str = "",
                output: str = "",
                encoding: str = "utf-8",
                overwrite: bool = False,
        ):
            pass

        def calculate(
                self,
                number: float,
                operation: str = "",
                factor: float = 1.0,
                precision: str = "medium",
                round: int = 0,
        ):
            pass

        def check(
                self,
                email: str,
                domain_check: bool = False,
                format_strict: bool = False,
                timeout: int = 30,
                retry: int = 1,
        ):
            pass

        def api(self):
            return self

        def get(
                self,
                endpoint: str,
                headers: str = "",
                params: str = "",
                timeout: int = 30,
                retry: int = 1,
        ):
            pass

        def config(self):
            return self

        def set(
                self,
                key: str,
                value: str,
                type: str = "string",
                env: str = "development",
                global_: bool = False,
                force: bool = False,
        ):
            pass

    return FireApp()


def setup_cloup() -> Any:
    @cloup.group()
    def cli():
        pass

    @cli.command()
    @cloup.argument("num", type=int)
    def hello(num):
        pass

    @cli.command()
    @cloup.argument("num", type=int)
    @cloup.option("--verbose", is_flag=True)
    def subcmd(num, verbose):
        pass

    @cli.command()
    @cloup.argument("value", type=int)
    @cloup.option("--min", type=int, default=0)
    @cloup.option("--max", type=int, default=100)
    @cloup.option("--name", type=str)
    def validate(value, min, max, name):
        pass

    # Новые команды для дополнительных сценариев
    @cli.group()
    def group():
        pass

    @group.group()
    def subgroup():
        pass

    @subgroup.command()
    @cloup.option("--flag1", is_flag=True)
    @cloup.option("--option", type=str)
    @cloup.option("--list", type=str)
    def command(flag1, option, list):
        pass

    @cli.command()
    @cloup.option("--input", type=str, required=True)
    @cloup.option("--output", type=str, required=True)
    @cloup.option("--encoding", type=str, default="utf-8")
    @cloup.option("--overwrite", is_flag=True)
    def process(input, output, encoding, overwrite):
        pass

    @cli.command()
    @cloup.argument("number", type=float)
    @cloup.option("--operation", type=str, required=True)
    @cloup.option("--factor", type=float, default=1.0)
    @cloup.option("--precision", type=str, default="medium")
    @cloup.option("--round", type=int, default=0)
    def calculate(number, operation, factor, precision, round):
        pass

    @cli.command()
    @cloup.argument("email", type=str)
    @cloup.option("--domain-check", is_flag=True)
    @cloup.option("--format-strict", is_flag=True)
    @cloup.option("--timeout", type=int, default=30)
    @cloup.option("--retry", type=int, default=1)
    def check(email, domain_check, format_strict, timeout, retry):
        pass

    @cli.group()
    def api():
        pass

    @api.command()
    @cloup.argument("endpoint", type=str)
    @cloup.option("--headers", type=str)
    @cloup.option("--params", type=str)
    @cloup.option("--timeout", type=int, default=30)
    @cloup.option("--retry", type=int, default=1)
    def get(endpoint, headers, params, timeout, retry):
        pass

    @cli.group()
    def config():
        pass

    @config.command()
    @cloup.argument("key", type=str)
    @cloup.argument("value", type=str)
    @cloup.option("--type", type=str, default="string")
    @cloup.option("--env", type=str, default="development")
    @cloup.option("--global_", is_flag=True)
    @cloup.option("--force", is_flag=True)
    def set(key, value, type, env, global_, force):
        pass

    return cli


def execute_click(cli: Any, command: str) -> None:
    with mock_argv(["cli", *command.split()]):
        cli(standalone_mode=False)


def execute_typer(app: Any, command: str) -> None:
    with mock_argv(["cli", *command.split()]):
        try:
            app()
        except SystemExit:
            pass


def execute_spaceworld(cns: Any, command: str) -> None:
    with mock_argv(["cli", *command.split()]):
        try:
            cns()
        except SystemExit:
            pass


def execute_argparse(parser: Any, command: str) -> None:
    with mock_argv(["cli", *command.split()]):
        parser.parse_args()


def execute_fire(FireApp: Any, command: str) -> None:
    with mock_argv(["cli", *command.split()]):
        try:
            fire.Fire(FireApp)
        except SystemExit:
            pass


def execute_cloup(cli: Any, command: str) -> None:
    """Выполнение команды Cloup"""
    with mock_argv(["cli", *command.split()]):
        try:
            cli.main()
        except SystemExit:
            pass


@contextmanager
def mock_argv(args: list[str]):
    """Контекстный менеджер для подмены sys.argv"""
    original = sys.argv
    sys.argv = args
    try:
        yield
    finally:
        sys.argv = original


@run
def main(
        runs: Annotated[int, lambda runs: runs >= 1] = 1,
        warmup: Annotated[int, lambda runs: runs >= 1] = 1,
        memory: bool = True,
        profile: bool = False,
):
    """Основная функция"""
    try:
        runner = BenchmarkRunner()

        runner.add_library(
            BenchmarkLibrary("spaceworld", setup_spaceworld, execute_spaceworld)
        )
        runner.add_library(
            BenchmarkLibrary("argparse", setup_argparse, execute_argparse)
        )

        runner.add_library(BenchmarkLibrary("click", setup_click, execute_click))
        runner.add_library(BenchmarkLibrary("typer", setup_typer, execute_typer))

        runner.add_library(BenchmarkLibrary("cloup", setup_cloup, execute_cloup))
        runner.add_library(BenchmarkLibrary("fire", setup_fire, execute_fire))
        runner.config.update(
            {"runs": runs, "warmup": warmup, "memory": memory, "profile": profile}
        )

        print_welcome(runner.scenarios, set(runner.libraries.keys()))

        runner.run_benchmarks()

        runner.print_results()

    except Exception as e:
        console.print(f"\n[red]Error: {e}")
        traceback.print_exc()
        sys.exit(1)
