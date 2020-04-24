import os
import pipes
import subprocess
import tempfile


def get_output(cmd_list, cwd, valid_return_codes=(0,)):
    """Return command output as a list of non-empty lines."""
    res = subprocess.run(
        cmd_list,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        encoding="utf-8",
    )
    if res.returncode not in valid_return_codes:
        raise subprocess.CalledProcessError(
            res.returncode, cmd_list, res.stdout, res.stderr,
        )
    # Remove empty lines.
    return list(filter(bool, res.stdout.split(os.linesep)))


def get_pipe_command_output(base_cmd_list, piped_to, cwd=None, valid_return_codes=(0,)):
    """Return output of ``base_cmd_list | piped_to`` as a list of
    non-empty lines.
    """
    _fp, pipefile_path = tempfile.mkstemp()
    try:
        pipe = pipes.Template()
        pipe.append(piped_to, "--")
        pipefile = pipe.open(pipefile_path, "w")
        command_output = get_output(
            base_cmd_list, cwd=cwd, valid_return_codes=valid_return_codes
        )
        pipefile.write(os.linesep.join(command_output))
        pipefile.close()
        lines = open(pipefile_path).read().split(os.linesep)
        return list(filter(bool, lines))
    finally:
        if not pipefile.closed:  # pragma: no cover
            pipefile.close()
        os.unlink(pipefile_path)
