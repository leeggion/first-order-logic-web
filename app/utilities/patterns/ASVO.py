from .base import Base


class ASVO(Base):
    def match(self, doc):
        raise NotImplementedError

    def convert(self, doc):
        raise NotImplementedError
