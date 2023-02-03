"""https://stackoverflow.com/questions/6893968/how-to-get-the-return-value-from-a-thread """
from threading import Thread


class ThreadWithReturnValue(Thread):
    """https://stackoverflow.com/questions/6893968/how-to-get-the-return-value-from-a-thread """
    def __init__(self, group=None, target=None, name=None,
                 args:tuple = None, kwargs:dict = None):
        super().__init__( group, target, name, args, kwargs)

        #super().__init__(group, target, name, args, kwargs)
        self._return = None
        self._target = target
        self._args = args
        self._kwargs = kwargs
        #        self._args = args
        #        self._kwargs = kwargs

    def run(self):
        try:
            if self._target is not None:
                if self._kwargs is None:
                    self._return = self._target(*self._args)
                else:
                    self._return = self._target(*self._args, **self._kwargs)
        finally:
            # Avoid a refcycle if the thread is running a function with
            # an argument that has a member that points to the thread.
            del self._target, self._args, self._kwargs



    def join(self, timeout=None):
        super().join(timeout)
        return self._return
