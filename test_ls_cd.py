from unittest import TestCase, mock
from unittest.mock import Mock
from io import StringIO
import pathlib

from commands import Ls, Cd


class TestLs(TestCase):

    @mock.patch("os.listdir", return_value=["dir1", "dir2"])
    def test_ls_call_os_listdir_command(self, ls_mock : Mock):
        out_stream = StringIO("")
        ls = Ls(OutputStream=out_stream)
        ls.exec([])

        self.assertEqual(
            out_stream.getvalue(),
            "dir1\ndir2\n"
        )

        ls_mock.assert_called_once()


class TestCd(TestCase):

    @mock.patch("os.chdir", return_value=None)
    def test_cd_call_chdir_command(self, cd_mock : Mock):
        new_dir = "/home"
        out_stream = StringIO("")
        cd = Cd(OutputStream=out_stream)
        cd.exec(new_dir)

        cd_mock.assert_called_once()

    @mock.patch("os.chdir", return_value=None)
    def test_cd_call_chdir_command(self, cd_mock: Mock):
        new_dir = "/home"
        out_stream = StringIO("")
        cd = Cd(OutputStream=out_stream)
        cd.exec(new_dir)

        cd_mock.assert_called_once_with(pathlib.Path(new_dir))
