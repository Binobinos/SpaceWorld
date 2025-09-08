from spaceworld import SpaceWorld
from spaceworld import annotation_depends


def test_annotation_depends():
    def add(a: int, b: int):
        return a + b

    assert annotation_depends(add)("2", "2") == 4


class TestSpaceWorld:
    def test_module(self) -> None:
        """Testing SpaceWorld.module"""
        cns = SpaceWorld()

        def module():
            """The module for the test"""

        _module = cns.module(module)
        assert _module.name == "module"
        assert _module.docs == "The module for the test"

        new_module = cns.module(name="new_module",
                                docs="Documentation module")(module)
        assert new_module.name == "new_module"
        assert new_module.docs == "Documentation module"

    def test_command(self) -> None:
        """Testing SpaceWorld.command"""
        cns = SpaceWorld()

        def command():
            """The module for the test"""

    def test__check_mode(self) -> None:
        """Testing SpaceWorld._check_mode"""

    def test__get_cached_args(self) -> None:
        """Testing SpaceWorld._get_cached_args"""

    def test__get_command_cache(self) -> None:
        """Testing SpaceWorld._get_command_cache"""

    def test__handle_confirm(self) -> None:
        """Testing SpaceWorld._handle_confirm"""

    def test__handle_confirmation(self) -> None:
        """Testing SpaceWorld._handle_confirmation"""

    def test__is_cached(self) -> None:
        """Testing SpaceWorld._is_cached"""

    def test__register_command(self) -> None:
        """Testing SpaceWorld._register_command"""

    def test__register_module(self) -> None:
        """Testing SpaceWorld._register_module"""

    def test__search_command(self) -> None:
        """Testing SpaceWorld._search_command"""

    def test__set_confirm_command(self) -> None:
        """Testing SpaceWorld._set_confirm_command"""

    def test__write_deprecated(self) -> None:
        """Testing SpaceWorld._write_deprecated"""

    def test__write_help(self) -> None:
        """Testing SpaceWorld._write_help"""

    def test_error_handler(self) -> None:
        """Testing SpaceWorld.error_handler"""

    def test_execute(self) -> None:
        """Testing SpaceWorld.execute"""

    def test_execute_command(self) -> None:
        """Testing SpaceWorld.execute_command"""

    def test_get_handler(self) -> None:
        """Testing SpaceWorld.get_handler"""

    def test_handler(self) -> None:
        """Testing SpaceWorld.handler"""

    def test_include(self) -> None:
        """Testing SpaceWorld.include"""

    def test_interactive(self) -> None:
        """Testing SpaceWorld.interactive"""

    def test_run(self) -> None:
        """Testing SpaceWorld.run"""

    def test_set_mode(self) -> None:
        """Testing SpaceWorld.set_mode"""

    def test_spaceworld(self) -> None:
        """Testing SpaceWorld.spaceworld"""
