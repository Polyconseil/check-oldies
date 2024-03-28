import enum


__all__ = ["StrEnum"]

try:
    from enum import StrEnum
except ImportError:  # Python < 3.11
    # fmt: off
    # pylint: disable=consider-using-f-string
    # Lifted from Python standard library, with docstrings removed for brevity.
    # https://github.com/python/cpython/blob/c1712ef066321c01bf09cba3f22fc474b5b8dfa7/Lib/enum.py
    class StrEnum(str, enum.Enum):
        def __new__(cls, *values):
            "values must already be of type `str`"
            if len(values) > 3:
                raise TypeError('too many arguments for str(): %r' % (values, ))
            if len(values) == 1:
                # it must be a string
                if not isinstance(values[0], str):
                    raise TypeError('%r is not a string' % (values[0], ))
            if len(values) >= 2:
                # check that encoding argument is a string
                if not isinstance(values[1], str):
                    raise TypeError('encoding must be a string, not %r' % (values[1], ))
            if len(values) == 3:
                # check that errors argument is a string
                if not isinstance(values[2], str):
                    raise TypeError('errors must be a string, not %r' % (values[2]))
            value = str(*values)
            member = str.__new__(cls, value)
            member._value_ = value
            return member

        @staticmethod
        def _generate_next_value_(name, start, count, last_values):
            return name.lower()
    # fmt: on
