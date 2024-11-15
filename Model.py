import random
import time

from collections import defaultdict
from typing import Type, List, Dict

import numpy as np

from System import System
from Generator import Generator
from Disposer import Disposer



class Model:
    def __init__(self,
                 generator: Generator,
                 disposer: Disposer,
                 primary_systems: list,
                 secondary_systems: list,
                 activation_threshold: int = 3,
                 ):

        self.generator: Generator = generator
        self.disposer: Disposer = disposer
        self.systems: List[System] = primary_systems + secondary_systems
        self.current_time: float = 0
        self.activation_threshold: int = activation_threshold
        self.binded_systems: List[(Type[System], Type[System])] = []
        self.transitions: Dict[(Type[System], Type[System]):float] = {}
    def _get_transition_probabilities(self, sender_system: Type[System]):
        '''
        Оскільки на вторинному етапі обробки частина верстатів не працює - сума значень ймовірностей переходів до таких верстатів
        рівномірно розподіляється між іншими працюючими верстатами вторинної обробки.
        Це потрібно для подальшого коректного вибору маршруту,
        адже ймовірність браку не змінюється, а при неактивності якогось верстату загальна сума ймовірностей переходів буде менша 1.
        Таким чином для вхідних параметрів задачі згідно варіанту завжди будемо отримувати ймовірність браку й переходу
        на другий вестат первинної обробки рівно заданому значенню, а ймовірність переходу до вільного верстату вторинної обробки рівну
        1-ймовірність_браку, себто 0.04 та 0.96 для відправки з першого верстату та 0.08 і 0.92 для відправки з другого.
        '''
        # Фільтруємо всі переходи для заданої системи-віддавача
        possible_transitions = [
            (receiver, prob) for (sender, receiver), prob in self.transitions.items()
            if sender == sender_system and receiver.is_active
        ]

        # Знаходимо загальну ймовірність неактивних переходів
        inactive_probability = sum(
            prob for (sender, receiver), prob in self.transitions.items()
            if sender == sender_system and not receiver.is_active
        )

        # Отримуємо активні системи-приймачі типу "secondary" і їхню кількість
        active_secondary_transitions = [
            (receiver, prob) for receiver, prob in possible_transitions if receiver.type == "secondary"
        ]
        num_active_secondaries = len(active_secondary_transitions)

        # Розподіляємо ймовірність неактивних переходів, якщо є активні системи "secondary"
        if num_active_secondaries > 0:
            equal_share = inactive_probability / num_active_secondaries
            possible_transitions = [
                (receiver, prob + equal_share) if receiver.type == "secondary" else (receiver, prob)
                for receiver, prob in possible_transitions
            ]
        return zip(*possible_transitions)

    def route_detail(self):
        for sender_system in self.systems:
            detail = sender_system.get_detail_out()

            if detail:

                receiver_systems, probabilities = self._get_transition_probabilities(sender_system)

                # Вибираємо систему-приймач з урахуванням ймовірностей
                receiver_system = random.choices(receiver_systems, weights=probabilities, k=1)[0]

                if receiver_system.type == "reworker":
                    detail.to_rework = True

                if detail.number_of_reworks == 1 and detail.to_rework:
                    self.disposer.set_waste(detail)
                    continue

                receiver_system.receive_detail(detail)

    def _check_transition_probabilities(self):
        probabilities_sum = defaultdict(float)

        # Проходимо по всіх переходах і додаємо ймовірності для кожної системи-віддавача
        for (sender_system, _), probability in self.transitions.items():
            probabilities_sum[sender_system] += probability

        # Перевіряємо, що сума ймовірностей для кожної системи-віддавача дорівнює 1
        for sender_system, total_probability in probabilities_sum.items():
            if not np.isclose(total_probability, 1.0):
                print(f"Помилка: сума ймовірностей для системи {sender_system} дорівнює {total_probability}, а не 1.")
                return False

        return True

    def bind(self, system_1: System, system_2: System):
        if system_1.type == system_2.type == "secondary":
            self.binded_systems.append((system_1, system_2))
        else:
            raise TypeError("Можна зв'язати лише системи вторинної обробки")

    def _update_binded_systems(self):
        for systems in self.binded_systems:
            if systems[0].get_queue_size() > self.activation_threshold > systems[1].get_queue_size():
                systems[0].block()
                systems[1].unblock()
            elif systems[0].get_queue_size() < self.activation_threshold:
                systems[0].unblock()
                systems[1].block()

    def update(self, time_diff):

        self._update_binded_systems()

        for system in self.systems:
            system.update(time_diff)

    def make_step(self):

        next_events = [system.get_next_event_time() for system in self.systems]
        next_system_index = next_events.index(min(next_events))

        if self.generator.get_next_event_time() < min(next_events):
            time_passed = self.generator.get_next_event_time()
            self.handle_input()
        else:
            time_passed = self.systems[next_system_index].process()

        return time_passed

    def log(self):
        print(f"Log for time: ", self.current_time)
        for system in self.systems:
            print(system)

    def statistical_report(self):
        workloads = []
        for system in self.systems:
            workloads.append(system.statistical_report(self.current_time))
        print("Total detail amount: ", self.generator.element_id)
        print("Total processed details ", len(self.disposer.processed_details))
        print("Total wastes", len(self.disposer.wastes))

        results = {"processed": len(self.disposer.processed_details),
                   "wastes": len(self.disposer.wastes),
                   "workloads": workloads}

        return results

    def simulate(self, simulation_time: float):

        while self.current_time < simulation_time:
            passed_time = self.make_step()
            self.route_detail()
            self.update(passed_time)
            self.current_time += passed_time
            #self.log()
        return self.statistical_report()

    def handle_input(self):
        detail = self.generator.process()
        idx = 1 if np.random.rand() < 0.5 else 0
        self.systems[idx].receive_detail(detail)

    def set_transitions(self, transitions):
        if not self._check_transition_probabilities():
            raise ValueError("Transition probabilities are incorrect")
        else:
            self.transitions = transitions

