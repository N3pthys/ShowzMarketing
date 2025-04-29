import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import seaborn as sns

def load_data():
    visits = pd.read_csv('../data/interim/visits_cleaned.csv')
    orders = pd.read_csv('../data/interim/orders_cleaned.csv')
    costs = pd.read_csv('../data/interim/costs_cleaned.csv')

    # Ensure datetime conversion
    if 'order_date' in orders.columns:
        orders['order_date'] = pd.to_datetime(orders['order_date'], errors='coerce')
    elif 'Buy Ts' in orders.columns:
        orders['order_date'] = pd.to_datetime(orders['Buy Ts'], errors='coerce')

    if 'user_id' not in orders.columns and 'Uid' in orders.columns:
        orders['user_id'] = orders['Uid']

    if 'amount' not in orders.columns and 'Revenue' in orders.columns:
        orders['amount'] = orders['Revenue']

    return visits, orders, costs

def create_cohort_table(orders):
    orders['cohort_month'] = orders.groupby('user_id')['order_date'].transform('min').dt.to_period('M')
    orders['order_month'] = orders['order_date'].dt.to_period('M')
    cohort_data = orders.groupby(['cohort_month', 'order_month']).agg(n_users=('user_id', 'nunique')).reset_index()
    cohort_pivot = cohort_data.pivot(index='cohort_month', columns='order_month', values='n_users').fillna(0)
    return cohort_pivot

def compute_ltv(orders):
    orders['cohort_month'] = orders.groupby('user_id')['order_date'].transform('min').dt.to_period('M')
    orders['order_month'] = orders['order_date'].dt.to_period('M')
    ltv = orders.groupby(['cohort_month', 'order_month']).agg(revenue=('amount', 'sum')).reset_index()
    ltv_pivot = ltv.pivot(index='cohort_month', columns='order_month', values='revenue').fillna(0)
    return ltv_pivot

def summarize_marketing_costs(costs):
    possible_channel_cols = ['channel', 'Channel', 'source_id', 'source']
    possible_cost_cols = ['cost', 'Cost', 'amount_spent', 'costs']

    channel_col = next((col for col in possible_channel_cols if col in costs.columns), None)
    cost_col = next((col for col in possible_cost_cols if col in costs.columns), None)

    if not channel_col or not cost_col:
        raise ValueError(f"Missing required columns. Found columns: {costs.columns.tolist()}")

    summary = costs.groupby(channel_col).agg(total_cost=(cost_col, 'sum')).reset_index()
    return summary

def save_processed_tables(cohort_table, ltv_table, marketing_summary):
    os.makedirs('../data/processed', exist_ok=True)
    cohort_table.to_csv('../data/processed/cohort_table.csv')
    ltv_table.to_csv('../data/processed/ltv_table.csv')
    marketing_summary.to_csv('../data/processed/marketing_summary.csv')

def plot_cohort_heatmap(cohort_table):
    plt.figure(figsize=(12, 8))
    sns.heatmap(cohort_table, annot=True, fmt=".0f", cmap="YlGnBu")
    plt.title("Cohort Analysis - User Retention")
    plt.ylabel("Cohort Month")
    plt.xlabel("Order Month")
    plt.tight_layout()
    plt.savefig("../data/processed/cohort_heatmap.png")
    plt.close()

def plot_ltv_line_chart(ltv_table):
    plt.figure(figsize=(12, 6))
    ltv_table.T.plot(legend=False)
    plt.title("Customer Lifetime Value Over Time")
    plt.xlabel("Order Month")
    plt.ylabel("Revenue")
    plt.tight_layout()
    plt.savefig("../data/processed/ltv_chart.png")
    plt.close()

if __name__ == "__main__":
    visits, orders, costs = load_data()
    cohort_table = create_cohort_table(orders)
    ltv_table = compute_ltv(orders)
    marketing_summary = summarize_marketing_costs(costs)

    save_processed_tables(cohort_table, ltv_table, marketing_summary)
    plot_cohort_heatmap(cohort_table)
    plot_ltv_line_chart(ltv_table)
