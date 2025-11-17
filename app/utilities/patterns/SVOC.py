from .base import Base


class SVOC(Base):
    def match(self, doc):
        raise NotImplementedError

    def convert(self, doc):
        raise NotImplementedError
