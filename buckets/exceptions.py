class InvalidPayload(BaseException):
    def __init__(self, errors={}, *args, **kwargs):
        super(InvalidPayload, self).__init__(*args, **kwargs)
        self.errors = errors
