from .base import Base


class ASVIODO(Base):
    def match(self, doc):
        raise NotImplementedError

    def convert(self, doc):
        raise NotImplementedError
