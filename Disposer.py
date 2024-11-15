from typing import List

from Element import Element
from Detail import Detail
class Disposer(Element):
    """
    Клас для збирання інформації про оброблені деталі та відходи
    """
    def __init__(self):
        super().__init__()
        self.processed_details: List[Detail] = []
        self.wastes: List[Detail] = []

    def receive_detail(self,
                       detail: Detail
                       ):
        """
        ОТримання обробленої деталі
        :param detail:
        :return:
        """
        self.processed_details.append(detail)

    def set_waste(self,
                  detail: Detail
                  ):
        """
        ОТримання деталі, яку визнано відоходом
        :param detail:
        :return:
        """
        self.wastes.append(detail)