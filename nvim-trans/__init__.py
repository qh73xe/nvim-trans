# -*- coding: utf-8 -*-
"""Neovim plugin for google translate."""
from typing import List, Union
from neovim import plugin, command

STRORNOT = Union[str, None]
STRS = List[str]
INTS = List[int]


def which_cmd(cmd: str) -> STRORNOT:
    """任意の SHELL コマンドが使用可能か否かを確認します.

    Args:
        cmd : 実行を確認したいコマンド名.

    Return:
        cmd が使用可能な場合にはそのコマンドのパスが,
        そうでない場合には, None がリターンされます.

    """
    from shutil import which
    if which(cmd):
        return cmd
    else:
        return None


def trans(target: str, sl: str='en', tl: str='ja', cmd: str='trans') -> STRS:
    """The translate function.

    Args:
        target : 翻訳を行う文字列
        sl (optional) : 変換前文字列の言語名
        tl (optional) : 変換後文字列の言語名
        cmd (optional) : 変換コマンド

    Examples:
        英語-日本語及び, 日本語-英語の翻訳を行います.

        >>> trans('hello')
        ['こんにちは']
        >>> trans('こんにちは', sl='ja', tl='en')
        ['hello']

    """
    from subprocess import Popen, PIPE
    cmds = [
        cmd, '-b', '-sl={}'.format(sl), '-tl={}'.format(tl), target
    ]
    proc = Popen(cmds, stdout=PIPE, stderr=PIPE)
    stdout_data, stderr_data = proc.communicate()
    if stderr_data:
        raise AssertionError(stderr_data.decode())
    else:
        return stdout_data.decode().split('\n')


@plugin
class TransPlugin(object):

    def __init__(self, nvim):
        self.nvim = nvim
        self.trans = 'trans'

    def _trans(self, target: str, sl: str='en', tl: str='ja') -> None:
        if which_cmd('trans'):
            res = trans(target, sl=sl, tl=tl)
            return '\n'.join(res)
        else:
            self.nvim.out_write(
                "{} is required.\n".format(
                    "Translate Shell"
                )
            )

    def echo(self, msg: str) -> None:
        self.nvim.command("echo '{}'".format(msg))

    def get_lines(self, ranges: INTS) -> str:
        stratLn, endLn = ranges
        if stratLn == endLn:
            line = self.nvim.current.line
        else:
            buff = self.nvim.current.buffer
            line = '\n'.join([
                buff[i]
                for i in range(stratLn, endLn)
            ])
        return line

    @command("TransEn2Ja", range='', nargs='*')
    def translate_en_ja(self, args, ranges):
        line = self.get_lines(ranges)
        res = self._trans(line)
        self.echo(res)

    @command("TransJa2En", range='', nargs='*')
    def translate_ja_en(self, args, ranges):
        line = self.get_lines(ranges)
        res = self._trans(line, sl='ja', tl='en')
        self.echo(res)
