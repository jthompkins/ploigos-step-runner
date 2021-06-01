"""Shared utils for dealing with gpg keys.
"""

import sh
import sys

from io import StringIO
from ploigos_step_runner.utils.io import create_sh_redirect_to_multiple_streams_fn_callback

def get_gpg_key(sig_file, extra_data_file, gpg_user):
    """Runs the step implemented by this StepImplementer.

    Returns
    -------
    StepResult
        Object containing the dictionary results of this step.
    """
    gpg_stdout_result = StringIO()
    gpg_stdout_callback = create_sh_redirect_to_multiple_streams_fn_callback([
        sys.stdout,
        gpg_stdout_result
    ])
    sh.gpg(
        '--armor',
        '-u',
        gpg_user,
        '--output',
        sig_file,
        '--detach-sign',
        extra_data_file,
        _out=gpg_stdout_callback,
        # _in=extra_data,
        _err_to_out=True,
        _tee='out'
    )
    return gpg_stdout_result