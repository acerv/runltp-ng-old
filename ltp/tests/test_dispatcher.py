"""
Unit tests for dispatcher implementations.
"""
import pytest
from ltp.common.events import Events
from ltp.dispatcher import DispatcherError
from ltp.dispatcher import SerialDispatcher
from ltp.sut import LocalSUTFactory


class DummyEvents(Events):
    """
    A dummy events class for dispatcher implementations.
    """


class TestSerialDispatcher:
    """
    Test SerialDispatcher class implementation.
    """

    def test_bad_constructor(self, tmpdir):
        """
        Test constructor with bad arguments.
        """
        factory = LocalSUTFactory()

        with pytest.raises(ValueError):
            SerialDispatcher(str(tmpdir), None, factory, DummyEvents())

        with pytest.raises(ValueError):
            SerialDispatcher(
                str(tmpdir),
                "this_folder_doesnt_exist",
                factory,
                DummyEvents())

        with pytest.raises(ValueError):
            SerialDispatcher(str(tmpdir), str(tmpdir), None, DummyEvents())

        with pytest.raises(ValueError):
            SerialDispatcher(str(tmpdir), str(tmpdir), factory, None)

    @pytest.mark.usefixtures("prepare_tmpdir")
    def test_exec_suites_bad_args(self, tmpdir):
        """
        Test exec_suites() method with bad arguments.
        """
        factory = LocalSUTFactory()
        dispatcher = SerialDispatcher(
            str(tmpdir),
            str(tmpdir),
            factory,
            DummyEvents())

        with pytest.raises(ValueError):
            dispatcher.exec_suites(None)

        with pytest.raises(DispatcherError):
            dispatcher.exec_suites(["this_suite_doesnt_exist"])

    @pytest.mark.usefixtures("prepare_tmpdir")
    def test_exec_suites(self, tmpdir):
        """
        Test exec_suites() method.
        """
        factory = LocalSUTFactory()
        dispatcher = SerialDispatcher(
            str(tmpdir),
            str(tmpdir),
            factory,
            DummyEvents())

        results = dispatcher.exec_suites(suites=["dirsuite0", "dirsuite2"])

        assert results[0].suite.name == "dirsuite0"
        assert results[0].tests_results[0].passed == 1
        assert results[0].tests_results[0].failed == 0
        assert results[0].tests_results[0].skipped == 0
        assert results[0].tests_results[0].warnings == 0
        assert results[0].tests_results[0].broken == 0
        assert results[0].tests_results[0].return_code == 0
        assert results[0].tests_results[0].exec_time > 0

        assert results[1].suite.name == "dirsuite2"
        assert results[1].tests_results[0].passed == 0
        assert results[1].tests_results[0].failed == 0
        assert results[1].tests_results[0].skipped == 1
        assert results[1].tests_results[0].warnings == 0
        assert results[1].tests_results[0].broken == 0
        assert results[1].tests_results[0].return_code == 0
        assert results[1].tests_results[0].exec_time > 0
