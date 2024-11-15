import numpy as np

from Detail import Detail
from Element import Element


class Server(Element):
    """
    Клас для предствлення обробного пристрою системи(каналу обробки)
    """

    def __init__(self,
                 service_time_scale: float
                 ):
        """

        :param service_time_scale: параметр експоненціального закону розподілу часу роботи
        """
        super().__init__()

        self.current_detail: Detail = None  # Поточна деталь на обробці
        self.service_time_scale: float = service_time_scale
        self.next_event_time: float = self.get_service_time()
        self.work_time: float  = 0  # Загальний час обробки деталей обробником

    def get_service_time(self) -> float:
        """
        Час роботи обробника
        :return: float
        """
        return np.random.exponential(self.service_time_scale)

    def process(self) -> float:
        """
        час обробки поточної деталі
        :return: float
        """
        passed_time = self.next_event_time
        self.next_event_time = np.inf
        self.work_time += passed_time
        if self.current_detail.to_rework:
            self.rework()
        return passed_time

    def update(self,
               time_diff: float
               ) -> None:
        """
        Оновлення часу обробки поточної деталі
        :param time_diff: Величина пройденого часу у моделі
        :return: None
        """
        self.work_time += time_diff
        self.next_event_time -= time_diff

    def rework(self):
        """
        Повторна обробка деталі за необхідності
        :return: None
        """
        self.current_detail.number_of_reworks += 1
        self.current_detail.to_rework = False

    def get_detail_out(self):
        """
        Отримання обробленої деталі і позначення обробника вільним
        :return: Detail
        """
        detail = self.current_detail
        self.current_detail = None
        return detail

    def set_detail(self, detail: Detail):
        """
        Установка деталі на обробку
        :param detail: деталь отримана на обробку
        :return: None
        """
        self.current_detail = detail
        self.next_event_time = self.get_service_time()

    def is_free(self):
        """
        Чи вільний поточний обробник
        :return: bool
        """
        return not self.current_detail

    def __repr__(self):
        return (f"Server with Service Time: {self.get_next_event_time()}, "
                f"Is free: {self.is_free()} "
                f"Current detail: {self.current_detail} ")
