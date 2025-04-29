# src/viz.py

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import os

def plot_dau(visits):
    visits['date'] = visits['Start Ts'].dt.date
    dau = visits.groupby('date')['Uid'].nunique()
    plt.figure(figsize=(12,6))
    dau.plot()
    plt.title('Usuarios Activos Diarios (DAU)')
    plt.xlabel('Fecha')
    plt.ylabel('Usuarios Únicos')
    plt.grid(True)
    plt.savefig('../reports/figures/dau.png')
    plt.close()

def plot_sessions_per_day(visits):
    visits['date'] = visits['Start Ts'].dt.date
    sessions = visits.groupby('date').size()
    plt.figure(figsize=(12,6))
    sessions.plot()
    plt.title('Sesiones por Día')
    plt.xlabel('Fecha')
    plt.ylabel('Número de Sesiones')
    plt.grid(True)
    plt.savefig('../reports/figures/sessions_per_day.png')
    plt.close()

def plot_session_duration(visits):
    visits['duration'] = (visits['End Ts'] - visits['Start Ts']).dt.total_seconds() / 60
    plt.figure(figsize=(12,6))
    sns.histplot(visits['duration'], bins=30, kde=True)
    plt.title('Distribución de Duración de Sesiones (minutos)')
    plt.xlabel('Duración (minutos)')
    plt.grid(True)
    plt.savefig('../reports/figures/session_duration.png')
    plt.close()

def plot_retention_curve(orders):
    orders['order_date'] = pd.to_datetime(orders['Buy Ts'])
    orders['cohort'] = orders.groupby('Uid')['order_date'].transform('min').dt.to_period('M')
    orders['order_month'] = orders['order_date'].dt.to_period('M')
    cohort_data = orders.groupby(['cohort', 'order_month']).agg(n_users=('Uid', 'nunique')).reset_index()
    cohort_pivot = cohort_data.pivot(index='cohort', columns='order_month', values='n_users')
    cohort_size = cohort_pivot.iloc[:,0]
    retention = cohort_pivot.divide(cohort_size, axis=0)
    plt.figure(figsize=(12,6))
    sns.heatmap(retention, annot=True, fmt='.0%', cmap='YlGnBu')
    plt.title('Curva de Retención por Cohorte')
    plt.xlabel('Mes de Pedido')
    plt.ylabel('Mes de Cohorte')
    plt.savefig('../reports/figures/retention_curve.png')
    plt.close()

def plot_ltv(orders):
    orders['order_date'] = pd.to_datetime(orders['Buy Ts'])
    orders['cohort'] = orders.groupby('Uid')['order_date'].transform('min').dt.to_period('M')
    orders['order_month'] = orders['order_date'].dt.to_period('M')
    ltv = orders.groupby(['cohort', 'order_month']).agg(revenue=('Revenue', 'sum')).reset_index()
    ltv_pivot = ltv.pivot(index='cohort', columns='order_month', values='revenue').fillna(0)
    plt.figure(figsize=(12,6))
    sns.heatmap(ltv_pivot, annot=True, fmt='.0f', cmap='YlGnBu')
    plt.title('LTV por Cohorte')
    plt.xlabel('Mes de Pedido')
    plt.ylabel('Mes de Cohorte')
    plt.savefig('../reports/figures/ltv_cohort.png')
    plt.close()

def plot_marketing_costs(costs):
    costs['dt'] = pd.to_datetime(costs['dt'])
    costs['month'] = costs['dt'].dt.to_period('M')
    monthly_costs = costs.groupby(['month', 'source_id']).agg(total_cost=('cost', 'sum')).reset_index()
    monthly_pivot = monthly_costs.pivot(index='month', columns='source_id', values='total_cost').fillna(0)
    monthly_pivot.plot(kind='bar', stacked=True, figsize=(12,6))
    plt.title('Gastos de Marketing Mensuales por Fuente')
    plt.xlabel('Mes')
    plt.ylabel('Costo Total')
    plt.legend(title='Fuente')
    plt.tight_layout()
    plt.savefig('../reports/figures/marketing_costs.png')
    plt.close()
