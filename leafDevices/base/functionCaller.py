from inspect import signature


class FunctionCaller:
    toCall = None
    paramCount = 0

    def __init__(self, toCall):
        self.toCall = toCall
        self.paramCount = len(signature(toCall).parameters)
