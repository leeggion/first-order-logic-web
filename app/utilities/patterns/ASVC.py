from .base import Base


class ASVC(Base):
    def match(self, doc):
        raise NotImplementedError

    def convert(self, doc):
        raise NotImplementedError
