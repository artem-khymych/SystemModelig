class Detail:
    """
    Клас для представлення об'єкту деталі
    """

    def __init__(self,
                 id: int
                 ):
        """

        :param id: ідентифікатор деталі
        """
        self.id: int = id
        self.to_rework: bool = False
        self.number_of_reworks: int = 0

    def __repr__(self):
        return f"Detail id {self.id}, number_of_reworks {self.number_of_reworks}, is to rework {self.to_rework} "
