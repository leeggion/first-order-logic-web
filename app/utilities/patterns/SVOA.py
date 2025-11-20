from .base import Base


class SVOA(Base):
    def match(self, doc):
        raise NotImplementedError

    def convert(self, doc):
        raise NotImplementedError
