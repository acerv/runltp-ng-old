"""
Tests for LTX python library.
"""
import signal
import threading
import pytest
from ltx import LTX
from ltx import LTXError


class TestLTX:
    """
    Test the LTX class implementation.
    """

    @pytest.fixture
    def ltx(self, executor):
        """
        LTX object to test.
        """
        stdin = executor.stdin.fileno()
        stdout = executor.stdout.fileno()

        yield LTX(stdin, stdout)

    @pytest.mark.parametrize("count", [1, LTX.TABLE_ID_MAXSIZE + 100])
    def test_ping(self, ltx, count):
        """
        Test PING command.
        """
        for _ in range(0, count):
            time_ns = ltx.ping()
            assert time_ns > 0

    def test_reserve(self, ltx):
        """
        Test table_id reservation.
        """
        for i in range(0, LTX.TABLE_ID_MAXSIZE):
            table_id = ltx.reserve()
            assert i == table_id

        with pytest.raises(LTXError):
            ltx.reserve()
            ltx.reserve()
            ltx.reserve()

    @pytest.mark.parametrize("count", [1, LTX.TABLE_ID_MAXSIZE + 100])
    def test_execute(self, ltx, count):
        """
        Test EXEC command.
        """
        for _ in range(0, count):
            table_id = ltx.reserve()

            stdout, time_ns, si_code, si_status = ltx.execute(
                table_id,
                "/usr/bin/uname",
                timeout=0.5)
            assert stdout == "Linux\n"
            assert time_ns > 0
            assert si_code == 1
            assert si_status == 0

    @pytest.mark.parametrize("count", [1, LTX.TABLE_ID_MAXSIZE + 100])
    def test_kill(self, ltx, count):
        """
        Test KILL command after EXEC command.
        """
        class SleepThread(threading.Thread):
            """
            Thread for testing purpose running sleep command using LTX.
            """
            stdout = ""
            time_ns = 0
            si_code = 0
            si_status = 0

            def run(self) -> None:
                self.stdout, \
                    self.time_ns, \
                    self.si_code, \
                    self.si_status = ltx.execute(
                        table_id,
                        "/usr/bin/sleep 4",
                        timeout=6)

        for _ in range(0, count):
            table_id = ltx.reserve()

            thread = SleepThread(daemon=True)
            thread.start()

            ltx.kill(table_id)

            thread.join()

            assert thread.stdout == ""
            assert thread.time_ns > 0
            assert thread.si_code == 2
            assert thread.si_status == signal.SIGKILL

    @pytest.mark.xfail(msg="Not implemented yet")
    @pytest.mark.parametrize("count", [1, LTX.TABLE_ID_MAXSIZE + 100])
    def test_env_no_table_id(self, ltx, count):
        """
        Test ENV command without table_id.
        """
        for _ in range(0, count):
            ltx.env(None, "HELLO", "world")

            table_id = ltx.reserve()
            stdout, time_ns, si_code, si_status = ltx.execute(
                table_id,
                "echo $HELLO",
                timeout=1)

            assert stdout == "world\n"
            assert time_ns > 0
            assert si_code == 1
            assert si_status == 0

    @pytest.mark.xfail(msg="Not implemented yet")
    @pytest.mark.parametrize("count", [1, LTX.TABLE_ID_MAXSIZE + 100])
    def test_env_with_table_id(self, ltx, count):
        """
        Test ENV command using table_id.
        """
        for _ in range(0, count):
            table_id = ltx.reserve()

            ltx.env(table_id, "HELLO", "world")
            stdout, time_ns, si_code, si_status = ltx.execute(
                table_id,
                "echo $HELLO",
                timeout=1)

            assert stdout == "world\n"
            assert time_ns > 0
            assert si_code == 1
            assert si_status == 0

    def test_get_file(self, tmp_path, ltx):
        """
        Test get_file method.
        """
        pattern = b'AaXa\x00\x01\x02Zz' * 2048

        myfile = tmp_path / "file.txt"
        myfile.write_bytes(pattern)

        data = ltx.get_file(myfile.as_posix())

        assert data == pattern

    def test_set_file(self, tmp_path, ltx):
        """
        Test set_file method.
        """
        pattern = b'AaXa\x00\x01\x02Zz' * 2048

        myfile = tmp_path / "file.txt"

        ltx.set_file(myfile.as_posix(), pattern)

        content = myfile.read_bytes()
        assert content == pattern
