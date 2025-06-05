"""othpc module."""

from .submit_function import SubmitFunction
from .utils import (
    TempSimuDir,
    make_report_file,
    make_summary_file,
    evaluation_error_log,
    load_cache,
    fake_load,
)

# To circumvent a bug in OpenTURNS 1.24
from openturns.coupling_tools import OTCalledProcessError as _OTCalledProcessError


def _OTCalledProcessError_str(self):
    err_msg = (":\n" + self.stderr[:200].decode()) if self.stderr is not None else ""
    return super(_OTCalledProcessError, self).__str__() + err_msg


import openturns as _ot
from packaging.version import Version

if Version(_ot.__version__) < Version("1.25"):
    _OTCalledProcessError.__str__ = _OTCalledProcessError_str

__all__ = [
    "SubmitFunction",
    "TempSimuDir",
    "make_report_file",
    "make_summary_file",
    "evaluation_error_log",
    "load_cache",
    "fake_load",
]
__version__ = "0.1"
