
import pandas as pd
from scipy.stats import f_oneway
import numpy as np

from Disposer import Disposer
from Generator import Generator
from Model import Model
from System import System


def create_model(param):
    generator = Generator(arrival_rate=50)
    disposer = Disposer()

    # Первинна обробка – два верстати з різними параметрами часу обробки та ймовірності браку
    primary_system_1 = System(type="primary", service_time_scale=40, server_amount=1)
    primary_system_2 = System(type="reworker", service_time_scale=60, server_amount=1)

    # Вторинна обробка – два верстати з умовою активації другого верстата
    secondary_system_1 = System(type="secondary", service_time_scale=100, server_amount=1, is_active=True)
    secondary_system_2 = System(type="secondary", service_time_scale=100, server_amount=1, is_active=False)

    transitions = {
        (primary_system_1, primary_system_2): 0.04,
        (primary_system_1, secondary_system_1): 0.48,
        (primary_system_1, secondary_system_2): 0.48,
        (primary_system_2, primary_system_2): 0.08,
        (primary_system_2, secondary_system_1): 0.46,
        (primary_system_2, secondary_system_2): 0.46,
        (secondary_system_1, disposer): 1,
        (secondary_system_2, disposer): 1
    }

    # Створюємо і запускаємо модель
    model = Model(generator,
                  disposer,
                  primary_systems=[primary_system_1, primary_system_2],
                  secondary_systems=[secondary_system_1, secondary_system_2],
                  activation_threshold=param)

    model.set_transitions(transitions)
    model.bind(secondary_system_1, secondary_system_2)
    return model

def get_mean_stats(sim_time, param =3):
    processed_runs = []
    wastes_runs = []
    workloads_runs = []

    RUNS = 20
    for i in range(RUNS):
        # Створюємо новий об'єкт моделі в кожній ітерації (якщо це потрібно)
        model = create_model(param)
        run_res = model.simulate(simulation_time=sim_time)

        # Зберігаємо результати кожного прогону
        processed_runs.append(run_res["processed"])
        wastes_runs.append(run_res["wastes"])
        workloads_runs.append(run_res["workloads"])

    # Обчислення середніх значень та стандартних відхилень (сигм)
    mean_processed = np.mean(processed_runs)
    sigma_processed = np.std(processed_runs)

    mean_wastes = np.mean(wastes_runs)
    sigma_wastes = np.std(wastes_runs)

    # Якщо workloads - це список значень для кожного сервера
    mean_workloads = np.mean(workloads_runs, axis=0)
    sigma_workloads = np.std(workloads_runs, axis=0)
    print("-"*10)
    print("Statistical data on results of modeling")
    print(f"Processed details: {mean_processed} +- {sigma_processed}")
    print(f"Wastes: {mean_wastes} +- {sigma_wastes}")
    print(f"Workloads for servers: {mean_workloads} +- {sigma_workloads}")
    print("-" * 10)


def ANOVA(RUNS=20, param_values=[1, 2, 3, 4, 5]):
    data = []

    for param in param_values:
        for i in range(RUNS):

            model = create_model(param)
            run_res = model.simulate(simulation_time=100_000)

            # Додаємо результати у вигляді рядка у data
            data.append({
                'param': param,
                'wastes': run_res["wastes"],
                'processed': run_res["processed"],
                'workload_2.2': run_res["workloads"][-1]
            })

    # Створюємо DataFrame із зібраних даних
    df = pd.DataFrame(data)

    print(df, "\n")

    #Проведення однофакторного дисперсійного аналізу
    wastes_data = [df[df['param'] == p]['wastes'] for p in param_values]

    f_stat_wastes, p_val_wastes = f_oneway(*wastes_data)
    print(f"ANOVA results for 'wastes': F={f_stat_wastes}, p={p_val_wastes}")

    workload_data = [df[df['param'] == p][f'workload_2.2'] for p in param_values]
    f_stat, p_val = f_oneway(*workload_data)
    print(f"ANOVA results for 'workload_2.2': F={f_stat}, p={p_val}")

    processed_data = [df[df['param'] == p][f'processed'] for p in param_values]
    f_stat, p_val = f_oneway(*processed_data)
    print(f"ANOVA results for processed details: F={f_stat}, p={p_val}")


def compare_models(simulation_time, runs=20):
    # Ініціалізуємо змінні для зберігання результатів
    results_model1 = {'processed': [], 'wastes': []}
    results_model2 = {'processed': [], 'wastes': []}

    # Запускаємо симуляцію для кожної моделі
    for _ in range(runs):

        model1 = create_model(3)

        model2 = create_model(3)
        model2.systems[0].type, model2.systems[1].type = model2.systems[1].type, model2.systems[0].type

        run_res1 = model1.simulate(simulation_time=simulation_time)
        results_model1['processed'].append(run_res1['processed'])
        results_model1['wastes'].append(run_res1['wastes'])

        # Прогін для моделі 2
        run_res2 = model2.simulate(simulation_time=simulation_time)
        results_model2['processed'].append(run_res2['processed'])
        results_model2['wastes'].append(run_res2['wastes'])

    # Перетворюємо результати на DataFrame для зручності аналізу
    df_model1 = pd.DataFrame(results_model1)
    df_model2 = pd.DataFrame(results_model2)
    print("\n","-"*10)
    print("Standart model processed ", df_model1['processed'].mean())
    print("Standart model wastes ", df_model1['wastes'].mean())

    print("Updated model processed ", df_model2['processed'].mean())
    print("Updated model wastes ", df_model2['wastes'].mean())
    # Ініціалізуємо словник для зберігання значень F та p для кожного параметра
    f_results = {}

    # Проводимо дисперсійний аналіз для кожного параметра
    for param in ['processed', 'wastes']:
        # Виконуємо тест Фішера
        f_value, p_value = f_oneway(df_model1[param], df_model2[param])
        f_results[param] = {'F-value': f_value, 'p-value': p_value}

        # Виводимо результати аналізу
        print(f"\nParameter: {param}")
        print(f"F-value: {f_value:.4f}, p-value: {p_value:.4f}")
