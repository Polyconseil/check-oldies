import os
import subprocess
import sys


try:
    import toml
except ImportError:  # pragma: no cover
    toml = None


PYPROJECT_FILENAME = "pyproject.toml"


def is_git_directory(path):
    res = subprocess.run(
        ["git", "rev-parse"],
        cwd=path,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    return res.returncode == os.EX_OK


def replace_dashes(options):
    """Recursively replace dashes by underscores in dictonary keys."""
    if not isinstance(options, dict):
        return options
    return {
        option.replace('-', '_'): replace_dashes(value)
        for option, value in options.items()
    }


def read_from_configuration_file(path, tool_name):
    if not toml:  # pragma: no cover
        sys.exit(
            'You must install with `pip install "check-oldies[toml]" '
            "to read from TOML configuration files."
        )
    try:
        conf = toml.load(path)
    except Exception as exc:  # pylint: disable=broad-except # pragma: no cover
        sys.exit("Error reading {}: {}".format(path, exc.args[-1]))

    if tool_name:
        try:
            options = conf["tool"][tool_name]
        except KeyError:  # pragma: no cover
            return {}
    else:
        options = conf

    return replace_dashes(options)


def get_config(
        tool_name,
        arg_parser,
        argv,
        config_class,
        config_file_default_name=PYPROJECT_FILENAME,
):
    """Get options from configuration file, possibly overriden by command
    line arguments.
    """
    args = arg_parser.parse_args(argv)
    if not args.conf and os.path.exists(config_file_default_name):
        args.conf = config_file_default_name
    config = {}
    if args.conf:
        config = read_from_configuration_file(args.conf, tool_name)
    # Override with command line arguments.
    for option, value in vars(args).items():
        if option != "conf" and value is not None:
            config[option] = value
    # Set defaults for missing settings and turn dict into an object.
    return config_class(**config)
