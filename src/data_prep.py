# src/data_prep.py

import pandas as pd
import os

def load_and_clean_visits(file_path):
    visits = pd.read_csv(file_path)
    visits['Start Ts'] = pd.to_datetime(visits['Start Ts'])
    visits['End Ts'] = pd.to_datetime(visits['End Ts'])
    visits['Uid'] = visits['Uid'].astype(str)
    visits['Source Id'] = visits['Source Id'].astype(str)
    visits = visits.drop_duplicates()
    visits = visits.dropna(subset=['Uid', 'Start Ts', 'End Ts'])
    return visits

def load_and_clean_orders(file_path):
    orders = pd.read_csv(file_path)
    orders['Buy Ts'] = pd.to_datetime(orders['Buy Ts'])
    orders['Uid'] = orders['Uid'].astype(str)
    orders = orders.drop_duplicates()
    orders = orders.dropna(subset=['Uid', 'Buy Ts', 'Revenue'])
    return orders

def load_and_clean_costs(file_path):
    costs = pd.read_csv(file_path)
    costs['dt'] = pd.to_datetime(costs['dt'])
    costs['source_id'] = costs['source_id'].astype(str)
    costs = costs.drop_duplicates()
    costs = costs.dropna()
    return costs

if __name__ == "__main__":
    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    visits = load_and_clean_visits(os.path.join(base_path, 'data/raw/visits_log_us.csv'))
    visits.to_csv(os.path.join(base_path, 'data/interim/visits_cleaned.csv'), index=False)

    orders = load_and_clean_orders(os.path.join(base_path, 'data/raw/orders_log_us.csv'))
    orders.to_csv(os.path.join(base_path, 'data/interim/orders_cleaned.csv'), index=False)

    costs = load_and_clean_costs(os.path.join(base_path, 'data/raw/costs_us.csv'))
    costs.to_csv(os.path.join(base_path, 'data/interim/costs_cleaned.csv'), index=False)
