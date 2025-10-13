from enum import Enum
from typing import Union

import pytest

from spaceworld import AnnotationManager, AnnotationsError
from spaceworld._types import Transformer, UserAny, TupleArgs, Args, Kwargs


@pytest.fixture
def manager():
    return AnnotationManager()


class TestEnum(Enum):
    test_1 = "test_1"
    test_2 = "test_2"
    test_3 = "test_3"


class TestAnnotationManager:
    def test__annotate_annotated(self) -> None:
        """Testing AnnotationManager._annotate_annotated"""

    def test__annotate_base_type(self) -> None:
        """Testing AnnotationManager._annotate_base_type"""

    def test__annotate_callable(self) -> None:
        """Testing AnnotationManager._annotate_callable"""

    @pytest.mark.parametrize(
        "enum, arg, expected, expect_error",
        [
            (TestEnum, "test_1", TestEnum.test_1, False),
            (TestEnum, "test_2", TestEnum.test_2, False),
            (TestEnum, "test_3", TestEnum.test_3, False),
            (TestEnum, "error", None, True),
            (TestEnum, "invalid_value", None, True),
        ],
    )
    def test__annotate_enum(
            self,
            manager: AnnotationManager,
            enum: type[Enum],
            arg: UserAny,
            expected: Enum | None,
            expect_error: bool,
    ) -> None:
        """Testing AnnotationManager._annotate_enum"""
        if expect_error:
            with pytest.raises(AnnotationsError):
                manager._annotate_enum(enum, arg)
        else:
            result = manager._annotate_enum(enum, arg)
            assert result == expected

    @pytest.mark.parametrize(
        "func, arg, expected",
        [
            (lambda x: x + " World!", "Hello", "Hello World!"),
            (lambda x: x + 2, 2, 4),
            (lambda x: x.upper(), "hello", "HELLO"),
            (lambda x: x * 10, 5, 50),
            (lambda x: x + [3], [1, 2], [1, 2, 3]),
            (lambda x: "Even" if x % 2 == 0 else "Odd", 4, "Even"),
            (lambda x: x(), lambda: 42, 42),
            (lambda x: str(x), None, "None"),
        ],
    )
    def test__annotate_lambda_transformer(
            self,
            manager: AnnotationManager,
            func: Transformer,
            arg: UserAny,
            expected: UserAny,
    ) -> None:
        """Testing AnnotationManager._annotate_lambda"""
        assert manager._annotate_lambda(func, arg) == expected

    def test__annotate_literal(self) -> None:
        """Testing AnnotationManager._annotate_literal"""

    def test__annotate_normal_type(self) -> None:
        """Testing AnnotationManager._annotate_normal_type"""

    @pytest.mark.parametrize(
        "annotation, arg, expected",
        [
            (Union[int, float, str], "123", 123),
            (Union[float, int, str], "123.123", 123.123),
            (Union[float, int, str], "hello", "hello"),
            (Union[int, str], "123", 123),
            (Union[int, float], "123.0", 123.0),
            (Union[int, float], "123", 123),
            (Union[int, bool], "1", 1),
            (Union[bool, int], "1", False),
            (Union[Union[int, float], str], "123", 123),
            (Union[Union[int, float], str], "123.123", 123.123),
        ],
    )
    def test__annotate_union_correct(
            self,
            manager: AnnotationManager,
            arg: UserAny,
            annotation: UserAny,
            expected: UserAny,
    ) -> None:
        """Testing AnnotationManager._annotate_union"""
        assert manager._annotate_union(annotation, arg) == expected

    def test__annotate_union_errors(self) -> None:
        """Testing AnnotationManager._annotate_union"""

    def test__convert_datetime(self) -> None:
        """Testing AnnotationManager._convert_datetime"""

    @pytest.mark.parametrize(
        "arg, expected",
        [
            ("true", True),
            ("Yes", True),
            ("Y", True),
            ("False", False),
            ("No", False),
            ("", False),
        ],
    )
    def test__convert_to_bool(
            self, manager: AnnotationManager, arg: TupleArgs, expected: Args
    ) -> None:
        """Testing AnnotationManager._convert_to_bool"""
        assert manager._convert_to_bool(arg) == expected

    def test__preparing_bool_flag(self) -> None:
        """Testing AnnotationManager._preparing_bool_flag"""

    def test__preparing_short_flag(self) -> None:
        """Testing AnnotationManager._preparing_short_flag"""

    def test__preparing_value_flag(self) -> None:
        """Testing AnnotationManager._preparing_value_flag"""

    def test_add_custom_transformer(self) -> None:
        """Testing AnnotationManager.add_custom_transformer"""

    def test_annotate(self) -> None:
        """Testing AnnotationManager.annotate"""

    @pytest.mark.parametrize(
        "arguments, expected_args, expected_kwargs",
        [
            (("arg1", "arg2"), ["arg1", "arg2"], {}),
            (("file.txt", "--flag"), ["file.txt"], {"flag": True}),
            (("--verbose",), [], {"verbose": True}),
            (("--no-verbose",), [], {"verbose": False}),
            (
                    ("--enable-logging", "--no-cache"),
                    [],
                    {"enable_logging": True, "cache": False},
            ),
            (("-xyz",), [], {"x": True, "y": True, "z": True}),
            (("-xYz",), [], {"x": True, "y": False, "z": True}),
            (("-XyZ",), [], {"x": False, "y": True, "z": False}),
            (("--user=admin",), [], {"user": "admin"}),
            (("--port=8080",), [], {"port": "8080"}),
            (("--message=Hello=World",), [], {"message": "Hello=World"}),
            (("--path=/home/user/docs",), [], {"path": "/home/user/docs"}),
            (
                    ("file.txt", "--user=guest", "-vV", "--no-color"),
                    ["file.txt"],
                    {"user": "guest", "v": False, "color": False},
            ),
            (
                    ("-abC", "--timeout=30", "input.txt"),
                    ["input.txt"],
                    {"a": True, "b": True, "c": False, "timeout": "30"},
            ),
            (("--text=Hello World!",), [], {"text": "Hello World!"}),
            (('--json=\'{"key":"value"}\'',), [], {"json": '{"key":"value"}'}),
            (("--flag", "--no-flag"), [], {"flag": False}),
            (("--color=red", "--color=blue"), [], {"color": "blue"}),
            (("-aA",), [], {"a": False}),
            (("--", "--not-a-flag"), [], {"not_a_flag": True}),
            (("",), [""], {}),
            (("--empty=",), [], {"empty": ""}),
        ],
    )
    def test_pre_preparing_arg(
            self,
            manager: AnnotationManager,
            arguments: TupleArgs,
            expected_args: Args,
            expected_kwargs: Kwargs,
    ) -> None:
        """Testing basic cases for AnnotationManager.pre_preparing_arg"""
        try:
            args, kwargs = manager.pre_preparing_arg(arguments)
        except ValueError as e:
            assert e.__str__() == "Invalid flag name: Empty name"
            return
        assert args == expected_args
        assert kwargs == expected_kwargs

    def test_preparing_annotate(self) -> None:
        """Testing AnnotationManager.preparing_annotate"""

    def test_preparing_args(self) -> None:
        """Testing AnnotationManager.preparing_args"""

    def test_preparing_default(self) -> None:
        """Testing AnnotationManager.preparing_default"""

    def test_preparing_var_keyword(self) -> None:
        """Testing AnnotationManager.preparing_var_keyword"""

    def test_preparing_var_positional(self) -> None:
        """Testing AnnotationManager.preparing_var_positional"""
