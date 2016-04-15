class InvalidPayload(BaseException):
    def __init__(self, errors={}, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.errors = errors
