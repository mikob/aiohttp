from collections.abc import MutableSequence
from inspect import signature

import asyncio


class Signal(MutableSequence):
    """A class for signals handling, a list for receivers.

    To connect a receiver coroutine to a signal, use the
    signal.append(receiver) method and family.

    For disconnecting just drop receiver from the list in preferable
    way, e.g. signal.remove(receiver) or del signal[recv_index]

    Signals are fired using yield from signal.send(), which takes
    named arguments.
    """

    def __init__(self, parameters):
        self._parameters = frozenset(parameters)
        self._receivers = []

    # all long following list of functions is here because I want make
    # Signal to be like-a-list but without .copy() and .sort()
    # also I'd like making the implementation fast.

    def __len__(self):
        return len(self._receivers)

    def __iter__(self):
        return iter(self._receivers)

    def __contains__(self, value):
        return value in self._receivers

    def __getitem__(self, index):
        return self._receivers[index]

    def __reversed__(self):
        return reversed(self._receivers)

    def __setitem__(self, index, receiver):
        assert not asyncio.iscoroutinefunction(receiver), receiver
        if __debug__:
            signature(receiver).bind(**{p: None for p in self._parameters})
        self._receivers[index] = receiver

    def __delitem__(self, index):
        del self._receivers[index]

    def insert(self, index, receiver):
        assert not asyncio.iscoroutinefunction(receiver), receiver
        if __debug__:
            signature(receiver).bind(**{p: None for p in self._parameters})
        self._receivers.insert(index, receiver)

    def append(self, receiver):
        # Check that the callback can be called with the given parameter names
        assert not asyncio.iscoroutinefunction(receiver), receiver
        if __debug__:
            signature(receiver).bind(**{p: None for p in self._parameters})
        self._receivers.append(receiver)

    def clear(self):
        self._receivers.clear()

    @asyncio.coroutine
    def send(self, **kwargs):
        """
        Sends data to all registered receivers.
        """
        for receiver in self._receivers:
            yield from receiver(**kwargs)
