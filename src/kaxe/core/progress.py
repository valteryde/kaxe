"""Progress bar helpers for terminal and notebook rendering."""

import time

import tqdm


class _NoProgress:
    def update(self, n=1):
        pass

    def close(self):
        pass


class _DeferredProgress:
    """Text progress bar that appears only after a time threshold."""

    def __init__(self, total, desc, threshold):
        self.total = total
        self.desc = desc
        self.threshold = threshold
        self.start = time.time()
        self.pbar = None
        self.count = 0

    def update(self, n=1):
        self.count += n
        if self.pbar is None and time.time() - self.start >= self.threshold:
            self.pbar = tqdm.tqdm(total=self.total, desc=self.desc, initial=self.count)
        if self.pbar is not None:
            self.pbar.update(n)

    def close(self):
        if self.pbar is not None:
            self.pbar.close()


def make_progress_bar(show, total, desc):
    from .window import settings, terminaltype

    if not show:
        return _NoProgress()
    if terminaltype == "terminal":
        return tqdm.tqdm(total=total, desc=desc)
    threshold = settings.get("jupyterLoadingThreshold", 1.0)
    return _DeferredProgress(total, desc, threshold)
