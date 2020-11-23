"""Exception classes
"""


class LfsError(RuntimeError):
    status_code = None

    def __init__(self, *args, **kwargs):
        if 'status_code' in kwargs:
            self.status_code = kwargs.pop('status_code')
        super(LfsError, self).__init__(*args, **kwargs)
