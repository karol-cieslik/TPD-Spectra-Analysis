"""Calculation progress state; widgets and worker threads never share Tk variables."""
from dataclasses import dataclass
from time import monotonic


def duration(seconds):
    seconds = max(0, int(seconds))
    return f'{seconds // 60:02d}:{seconds % 60:02d}'


@dataclass
class MonteCarloProgress:
    state: str = 'Idle'
    completed: int = 0
    total: int = 0
    started: float | None = None
    stopped: float | None = None
    detail: str = ''

    def start(self, total):
        self.state = 'Running'
        self.completed, self.total = 0, total
        self.started, self.stopped = monotonic(), None
        self.detail = ''

    def update(self, completed, total):
        if self.state not in ('Running', 'Cancelling'):
            return
        self.total = int(total)
        self.completed = min(self.total, max(self.completed, int(completed)))

    def finish(self, state, detail=''):
        self.state, self.detail = state, detail
        self.stopped = monotonic()

    def text(self):
        if self.started is None:
            return 'Idle — compare current models before Monte Carlo.', ''
        elapsed = (self.stopped if self.stopped is not None else monotonic()) - self.started
        percent = int(100 * self.completed / max(1, self.total))
        count = f'{self.state}: {self.completed} / {self.total} simulations completed ({percent}%)'
        timing = f'Elapsed {duration(elapsed)}'
        if self.state == 'Running' and self.completed and elapsed >= 1:
            remaining = elapsed * (self.total - self.completed) / self.completed
            timing += f' · estimated remaining {duration(remaining)}'
        elif self.state == 'Running':
            timing += ' · estimating remaining time…'
        return count, timing + (f' · {self.detail}' if self.detail else '')
