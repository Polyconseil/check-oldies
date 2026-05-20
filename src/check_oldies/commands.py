import os
import pathlib
import subprocess
import typing


def get_output(cmd_list, cwd, valid_return_codes=(0,)):
    """Return command output as a list of non-empty lines."""
    res = subprocess.run(
        cmd_list,
        cwd=cwd,
        capture_output=True,
        check=False,
        encoding="utf-8",
    )
    if res.returncode not in valid_return_codes:
        raise subprocess.CalledProcessError(
            res.returncode,
            cmd_list,
            res.stdout,
            res.stderr,
        )
    return [line for line in res.stdout.split(os.linesep) if line]


def get_pipe_command_output(
    base_cmd_list: list[str],
    piped_to: list[str],
    cwd: pathlib.Path,
    valid_return_codes: typing.Iterable[int] = (0,),
) -> list[str]:
    """Return output of ``base_cmd_list | piped_to`` as a list of
    non-empty lines.
    """
    # pylint: disable=consider-using-with
    pipe1 = subprocess.Popen(
        base_cmd_list,
        cwd=cwd,
        stdout=subprocess.PIPE,
        encoding="utf-8",
    )
    pipe2 = subprocess.Popen(
        piped_to,
        stdin=pipe1.stdout,
        stdout=subprocess.PIPE,
        encoding="utf-8",
    )
    pipe1.stdout.close()
    output = pipe2.communicate()[0]
    return [line for line in output.split(os.linesep) if line]
