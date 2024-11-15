import numpy as np
from Element import Element
from Detail import Detail


class Generator(Element):
    """
    Вхідний потік(генератор) заявок
    """

    def __init__(self,
                 arrival_rate: float
                 ):
        """
        :param arrival_rate: інтервал між надходженнями деталей
        """
        super().__init__()
        self.arrival_rate: float = arrival_rate
        self.element_id: int = 0
        self.calculate_next_detail_arrival_time()

    def calculate_next_detail_arrival_time(self):
        """
        Визначення часу наступного прибуття деталі
        :return:
        """

        self.next_event_time = np.random.exponential(self.arrival_rate)

    def process(self) -> Detail:
        """
        Генерування нової деталі
        :return: Detail
        """
        self.calculate_next_detail_arrival_time()
        self.element_id += 1
        return Detail(self.element_id)
