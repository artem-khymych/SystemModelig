class Element(object):
    """
    Клас для представлення об'єкту що існує у чаті і може виконувати якусь дію та оновлювати свій стан
    """

    def __init__(self):
        """

        """

        self.is_active: bool = True  # Чи активний поточний елемент
        self.type: str = None  # Тип поточного елементу
        self.next_event_time: float = 0  # Час до наступної події в елементі

    def update(self, time_diff: float):
        self.next_event_time -= time_diff

    def get_next_event_time(self):
        return self.next_event_time

    def process(self):
        pass
