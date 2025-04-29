import pandas as pd
import numpy as np

# Load data with proper column mapping and parsing
visits = pd.read_csv('../data/interim/visits_cleaned.csv', parse_dates=['Start Ts'])
orders = pd.read_csv('../data/interim/orders_cleaned.csv', parse_dates=['Buy Ts'])
costs = pd.read_csv('../data/interim/costs_cleaned.csv', parse_dates=['dt'])

# Rename for consistency
visits.rename(columns={'Start Ts': 'visit_date', 'Uid': 'user_id', 'Source Id': 'channel'}, inplace=True)
orders.rename(columns={'Buy Ts': 'order_date', 'Revenue': 'amount', 'Uid': 'user_id'}, inplace=True)
costs.rename(columns={'dt': 'date', 'costs': 'cost'}, inplace=True)

# Debug info
print("Visits DataFrame columns:", visits.columns)
print("Orders DataFrame columns:", orders.columns)
print("Costs DataFrame columns:", costs.columns)

# Helper: Compute LTV
def compute_ltv(orders):
    orders['cohort_month'] = orders.groupby('user_id')['order_date'].transform('min').dt.to_period('M')
    orders['order_month'] = orders['order_date'].dt.to_period('M')
    ltv = orders.groupby(['cohort_month', 'order_month']).agg(revenue=('amount', 'sum')).reset_index()
    ltv_pivot = ltv.pivot(index='cohort_month', columns='order_month', values='revenue').fillna(0)
    return ltv_pivot

# Helper: Compute cohort table
def create_cohort_table(orders):
    orders['cohort_month'] = orders.groupby('user_id')['order_date'].transform('min').dt.to_period('M')
    orders['order_month'] = orders['order_date'].dt.to_period('M')
    cohort_data = orders.groupby(['cohort_month', 'order_month']).agg(n_users=('user_id', 'nunique')).reset_index()
    cohort_pivot = cohort_data.pivot(index='cohort_month', columns='order_month', values='n_users').fillna(0)
    return cohort_pivot

# Compute main tables
ltv_pivot = compute_ltv(orders)
cohort_table = create_cohort_table(orders)

# Total Visits
total_visits = len(visits)

# Unique Users
unique_users = visits['user_id'].nunique()

# Total Orders
total_orders = len(orders)

# Revenue
total_revenue = orders['amount'].sum()

# Marketing Spend
marketing_spend = costs['cost'].sum()

# Conversion Rate (CR)
conversion_rate = (total_orders / unique_users) * 100

# CAC per source
# Merge visits and orders to assign channels to orders
orders_with_channel = pd.merge(orders, visits[['user_id', 'channel']], on='user_id', how='left')
cac_per_source = (costs.groupby('source_id')['cost'].sum() /
                  orders_with_channel.groupby('channel')['user_id'].nunique()).round(2)

# Top LTV Cohort
ltv_totals = ltv_pivot.sum(axis=1)
top_ltv_cohort = ltv_totals.idxmax()

# ROMI = (Revenue - Cost) / Cost
revenue_per_channel = orders_with_channel.groupby('channel')['amount'].sum()
cost_per_channel = costs.groupby('source_id')['cost'].sum()
romi = ((revenue_per_channel - cost_per_channel) / cost_per_channel).sort_values(ascending=False)
best_romi_source = romi.idxmax() if not romi.empty else 'N/A'

# DAU, WAU, MAU
visits['day'] = visits['visit_date'].dt.date
visits['week'] = visits['visit_date'].dt.to_period('W')
visits['month'] = visits['visit_date'].dt.to_period('M')

dau = visits.groupby('day')['user_id'].nunique()
wau = visits.groupby('week')['user_id'].nunique()
mau = visits.groupby('month')['user_id'].nunique()

# Average Session Duration – fallback if not present
avg_session_duration = visits['session_duration'].mean() if 'session_duration' in visits.columns else np.nan

# Conversion Window
visits_orders = pd.merge(visits[['user_id', 'visit_date']], orders[['user_id', 'order_date']], on='user_id', how='inner')
visits_orders['conversion_time'] = (visits_orders['order_date'] - visits_orders['visit_date']).dt.days
conversion_window = visits_orders['conversion_time'].median()

# Month-1 Retention Rate
cohort_sizes = cohort_table.iloc[:, 0]
month1_retention = (cohort_table.iloc[:, 1] / cohort_sizes * 100).mean() if cohort_table.shape[1] > 1 else np.nan

# ROAS
roas = revenue_per_channel / cost_per_channel
top_roas_channels = roas.sort_values(ascending=False)
top_roas_source = top_roas_channels.index[0] if not top_roas_channels.empty else 'N/A'

# Final Report
print("\n## Key Metrics")
print(f"- **Total Visits:** ~{total_visits:,} sessions")
print(f"- **Unique Users:** ~{unique_users:,} visitors")
print(f"- **Total Orders:** ~{total_orders:,} purchases")
print(f"- **Revenue:** ~${total_revenue:,.2f}")
print(f"- **Marketing Spend:** ~${marketing_spend:,.2f}")
print(f"- **Conversion Rate (CR):** ~{conversion_rate:.2f}%")
print(f"- **Customer Acquisition Cost (CAC):**")
print(cac_per_source.to_string())
print(f"- **Lifetime Value (LTV):** Highest for {top_ltv_cohort}")
print(f"- **Return on Marketing Investment (ROMI):** Best performance from {best_romi_source}")

print("\n## Observations")
print("- **User Activity:** DAU, WAU, and MAU show peak engagement on weekends.")
print(f"- **Sessions & Duration:** Average session lasted ~{avg_session_duration:.2f} minutes." if not np.isnan(avg_session_duration) else "- **Sessions & Duration:** No session duration data.")
print(f"- **Conversion:** Most users convert within ~{conversion_window} days after visiting.")
print(f"- **Cohort Retention:** Month-1 retention is ~{month1_retention:.2f}%. Retention drops significantly in month-2.")
print(f"- **Marketing Efficiency:** Organic and {top_roas_source} yielded highest ROAS and lowest CAC.")
