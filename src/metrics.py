# src/metrics.py

import pandas as pd

# VISITS METRICS

def calculate_dau(visits):
    return visits.groupby(visits['Start Ts'].dt.date)['Uid'].nunique()

def calculate_wau(visits):
    visits['week'] = visits['Start Ts'].dt.to_period('W')
    return visits.groupby('week')['Uid'].nunique()

def calculate_mau(visits):
    visits['month'] = visits['Start Ts'].dt.to_period('M')
    return visits.groupby('month')['Uid'].nunique()

def sessions_per_day(visits):
    return visits.groupby(visits['Start Ts'].dt.date)['Uid'].count()

def session_duration(visits):
    return (visits['End Ts'] - visits['Start Ts']).dt.total_seconds()

def returning_users(visits):
    user_counts = visits.groupby('Uid').size()
    return (user_counts > 1).sum()

# SALES METRICS

def conversion_days(visits, orders):
    first_visit = visits.groupby('Uid')['Start Ts'].min()
    first_order = orders.groupby('Uid')['Buy Ts'].min()
    conversion_time = (first_order - first_visit).dt.days
    return conversion_time

def orders_per_period(orders, freq='D'):
    return orders.set_index('Buy Ts').resample(freq)['Uid'].count()

def average_ticket_size(orders):
    return orders['Revenue'].mean()

def lifetime_value(orders):
    ltv = orders.groupby('Uid')['Revenue'].sum()
    return ltv

# MARKETING METRICS

def total_costs(costs):
    return costs.groupby('dt')['costs'].sum()

def cac_by_source(costs, orders, visits):
    first_visits = visits.groupby('Uid')['Source Id'].first().reset_index()
    merged = pd.merge(orders[['Uid']], first_visits, on='Uid', how='left')
    orders_by_source = merged.groupby('Source Id')['Uid'].count()
    costs_by_source = costs.groupby('source_id')['costs'].sum()
    cac = costs_by_source / orders_by_source
    return cac

def romi(costs, orders, visits):
    # Match orders to source
    first_visits = visits.groupby('Uid')['Source Id'].first().reset_index()
    merged = pd.merge(orders[['Uid', 'Revenue']], first_visits, on='Uid', how='left')
    revenue_by_source = merged.groupby('Source Id')['Revenue'].sum()
    cost_by_source = costs.groupby('source_id')['costs'].sum()
    romi = (revenue_by_source - cost_by_source) / cost_by_source
    return romi
