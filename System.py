from queue import Queue
import numpy as np

from Detail import Detail
from Server import Server
from Element import Element

np.random.exponential()


class System(Element):
    """
    Клас для представлення системи моделі
    """

    def __init__(self,
                 service_time_scale: float,
                 type="plain",
                 server_amount: int = 1,
                 max_queue_size: int = np.inf,
                 is_active: bool = True
                 ):
        """

        :param service_time_scale: Параметр експоненціального розподілу часу обробки деталі обробниками
        :param type: Тип системи
        :param server_amount: Кількість обробників
        :param max_queue_size: Максимальний розмір черги
        :param is_active: Чи активна система
        """
        super().__init__()

        self.servers = []
        for i in range(server_amount):
            self.servers.append(Server(service_time_scale))

        self.type: str = type
        self.queue = Queue(max_queue_size)
        self.next_event: System = None
        self.passed_time: float = 0
        self.detail_to_move: Detail = None

        self.is_active: bool = is_active
        # statistics
        self.failures: int = 0
        self.successes: int = 0
        self.workload: float = 0
        self.mean_queue_size: float = 0

    def get_next_event_time(self) -> float:
        """
        Отримання часу, через який станеться найближча подія у системі(найближча обробка деталі)
        :return: float
        """
        next_events = [server.get_next_event_time() if server.current_detail else np.inf for server in self.servers]
        next_event_index = next_events.index(min(next_events))

        if next_events[next_event_index] < np.inf:
            self.next_event = self.servers[next_event_index]
        else:
            self.next_event = None
        return self.next_event.next_event_time if self.next_event is not None else np.inf

    def update(self,
               time_diff: float
               ):
        """
        Оновлення станів обробників системи
        :param time_diff: Величина пройденого часу
        :return:
        """
        for server in self.servers:
            if not server.is_free():
                server.update(time_diff)
            elif server.current_detail is None:
                detail = self._queue_get()
                server.set_detail(detail)
        self.gather_statistics(time_diff)
    def statistical_report(self,
                           modeling_time: float
                           ):
        """
        Отримання статистичних даних системи
        :param modeling_time: час моделювання
        :return workload:
        """
        for server in self.servers:
            self.workload += server.work_time
        self.workload = self.workload / modeling_time / len(self.servers)
        print("----------------")
        print(f"System: {self.type}\n"
              f"workload: {self.workload},"
              f"mean queue size: {self.mean_queue_size / modeling_time},"
              f"successes: {self.successes}, failures: {self.failures} ")

        return self.workload

    def process(self) -> float:
        """
        Обробка деталі з найменшим часом обробки
        :return:
        """
        passed_time = self.next_event.process()
        detail = self.next_event.get_detail_out()
        self.successes += 1
        self.gather_statistics(passed_time)
        self.detail_to_move = detail

        return passed_time

    def get_detail_out(self):
        """
        Отримання обробленої деталі системою
        :return:
        """
        detail = self.detail_to_move if self.detail_to_move else None
        self.detail_to_move = None
        return detail

    def receive_detail(self,
                       detail: Detail
                       ):
        """
        ОТримання деталі на обробку
        :param detail: деталь для обробки
        :return:
        """
        if self.queue.qsize() < self.queue.maxsize:
            self.queue.put(detail)
        else:
            self.failures += 1

    def get_queue_size(self) -> int:
        """
        Отримання розміру черги системи
        :return:
        """
        return self.queue.qsize()

    def gather_statistics(self,
                          passed_time: float
                          ):
        """
        Збір інформації про середній розмір черги системи
        :param passed_time:
        :return:
        """
        self.mean_queue_size += self.queue.qsize() * passed_time

    def _queue_get(self):
        """
        Обробка отримання деталі із черги
        :return:
        """
        if self.queue.empty():
            return None
        else:
            return self.queue.get()

    def block(self):
        """
        Заблокувати маршрут до системи
        :return:
        """
        self.is_active = False

    def unblock(self):
        """
        Розблокувати маршрут до системи
        :return:
        """
        self.is_active = True

    def __repr__(self):
        return (
            f"Type: {self.type}, "
            f"Queue size: {self.queue.qsize()}, Max queue: {self.queue.maxsize}, "
            f"Servers: {self.servers}, "
            f"Workload: {self.workload}, "
            f"Failures: {self.failures}, "
            f"Successes: {self.successes}, "
            f"is active: {self.is_active}, ")
