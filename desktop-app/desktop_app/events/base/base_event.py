class BaseEvent:
    def type(self) -> str:
        return self.__class__.__name__

    @classmethod
    def event_type(cls) -> str:
        return cls.__name__
