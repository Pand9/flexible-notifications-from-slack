"""
Wraps 'notify-send' on ubuntu
"""
import subprocess

def _print_stdout(msg):
    print(msg, flush=True)


def _log_cmd_status(p, stdin=None):
    _print_stdout("Command %s ended with status %d" % (p.args, p.returncode))
    _print_stdout("-Stdout-")
    for line in p.stdout.split("\n"):
        _print_stdout(line.rstrip())
    _print_stdout("-Stderr-")
    for line in p.stderr.split("\n"):
        _print_stdout(line.rstrip())
    if stdin:
        _print_stdout("-Stdin-")
        for line in stdin.split("\n"):
            _print_stdout(line.rstrip())
    _print_stdout("-End-")


def emit_notification(title, message):
    # noinspection PyArgumentList
    p = subprocess.run(["notify-send", "--urgency=critical", title, message], capture_output=True, text=True)
    if p.returncode:
        _log_cmd_status(p)
    p.check_returncode()
