import logging

from tautbot.config import conf
from tautbot.logger import ClassPrefixAdapter


class Base(object):

    def __init__(self):
        self.conf = conf
        self.logger = ClassPrefixAdapter(prefix=self.__class__.__name__, logger=logging.getLogger(__name__))
