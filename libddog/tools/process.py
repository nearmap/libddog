import os
import subprocess
from typing import Dict, List, Optional


class CmdResult:
    def __init__(
        self,
        args: List[str],
        cwd: str,
        environ: Dict[str, str],
        exit_code: int,
        stdout: bytes,
        stderr: bytes,
    ) -> None:
        self.args = args
        self.cwd = cwd
        self.environ = environ
        self.exit_code = exit_code
        self.stdout = stdout
        self.stderr = stderr

    def __repr__(self) -> str:
        stdout = f"<<<{self.stdout!r}>>>"
        stderr = f"<<<{self.stderr!r}>>>"

        return "%s(args=%r, cwd=%r, environ=%r, exit_code=%r, stdout=%r, stderr=%r)" % (
            self.__class__.__name__,
            self.args,
            self.cwd,
            self.environ,
            self.exit_code,
            stdout,
            stderr,
        )

    def __str__(self) -> str:
        return self.__repr__()


def invoke(
    args: List[str], cwd: Optional[str] = None, environ: Optional[Dict[str, str]] = None
) -> CmdResult:
    cwd = cwd or os.getcwd()

    env = dict(os.environ)
    env.update(environ or {})

    proc = subprocess.Popen(
        args=args, cwd=cwd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    stdout, stderr = proc.communicate()

    return CmdResult(
        args=args,
        cwd=cwd,
        environ=env,
        exit_code=proc.returncode,
        stdout=stdout,
        stderr=stderr,
    )
