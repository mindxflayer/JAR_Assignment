# Question 1, Part 1: Sales and Profitability Analysis

import pandas as pd

# Load the data
orders = pd.read_excel("List of Orders.xlsx")
details = pd.read_excel("Order Details.xlsx")

# Merge on Order ID
merged = details.merge(orders, on="Order ID", how="left")

# Total sales and total profit for each category
summary = merged.groupby("Category").agg(
    Total_Sales=("Amount", "sum"),
    Total_Profit=("Profit", "sum"),
    Number_of_Orders=("Order ID", "nunique"),
).reset_index()

# Average profit per order = total profit / number of distinct orders in the category
summary["Average Profit Per Order"] = (summary["Total_Profit"] / summary["Number_of_Orders"]).round(2)

# Profit margin (%) = total profit / total sales * 100
summary["Profit Margin (%)"] = (summary["Total_Profit"] / summary["Total_Sales"] * 100).round(2)

summary = summary.rename(columns={"Total_Sales": "Total Sales", "Total_Profit": "Total Profit"})
summary = summary[["Category", "Total Sales", "Total Profit", "Average Profit Per Order", "Profit Margin (%)"]]

print(summary.to_string(index=False))

# Top and underperforming categories for each metric
for metric in ["Total Sales", "Average Profit Per Order", "Profit Margin (%)"]:
    best = summary.loc[summary[metric].idxmax(), "Category"]
    worst = summary.loc[summary[metric].idxmin(), "Category"]
    print(metric, "-> Top:", best, "| Underperforming:", worst)


# Question 1, Part 2: Target Achievement Analysis
print("\n--- Part 2: Furniture Target Analysis ---")

# Load the sales target data and keep only Furniture
targets = pd.read_excel("Sales target.xlsx")
furniture = targets[targets["Category"] == "Furniture"].copy()

# The rows are already in month order, so we do not sort by date.
furniture["Month"] = furniture["Month of Order Date"].dt.strftime("%b-%d")

# Month-over-month percentage change in target
furniture["Change (%)"] = (furniture["Target"].pct_change() * 100).round(2)

print(furniture[["Month", "Target", "Change (%)"]].to_string(index=False))

# Months with a larger than average change are treated as significant
average_change = furniture["Change (%)"].mean()
print("\nAverage monthly change (%):", round(average_change, 2))
print("Months with above-average change:")
print(furniture[furniture["Change (%)"] > average_change][["Month", "Change (%)"]].to_string(index=False))

# Question 1, Part 2: Target Achievement Analysis
print("\n--- Part 2: Furniture Target Analysis ---")

# Load the sales target data and keep only Furniture
targets = pd.read_excel("Sales target.xlsx")
furniture = targets[targets["Category"] == "Furniture"].copy()

# The rows are already in month order, so we do not sort by date.
furniture["Month"] = furniture["Month of Order Date"].dt.strftime("%b-%d")

# Month-over-month percentage change in target
furniture["Change (%)"] = (furniture["Target"].pct_change() * 100).round(2)

print(furniture[["Month", "Target", "Change (%)"]].to_string(index=False))

# Months with a larger than average change are treated as significant
average_change = furniture["Change (%)"].mean()
print("\nAverage monthly change (%):", round(average_change, 2))
print("Months with above-average change:")
print(furniture[furniture["Change (%)"] > average_change][["Month", "Change (%)"]].to_string(index=False))


# Question 1, Part 3: Regional Performance Insights
print("\n--- Part 3: Regional Performance ---")

# Top 5 states by order count (each Order ID appears once in the orders table)
top_states = orders["State"].value_counts().head(5).index

# Total sales, total profit and order count for each state (uses 'merged' from Part 1)
state_data = merged[merged["State"].isin(top_states)]
state_table = state_data.groupby("State").agg(
    Order_Count=("Order ID", "nunique"),
    Total_Sales=("Amount", "sum"),
    Total_Profit=("Profit", "sum"),
).reset_index()

# Average profit per order = total profit / number of orders
state_table["Average Profit Per Order"] = (state_table["Total_Profit"] / state_table["Order_Count"]).round(2)
state_table = state_table.sort_values("Order_Count", ascending=False)
print(state_table.to_string(index=False))

# Same figures for each city in the top 5 states
city_table = state_data.groupby(["State", "City"]).agg(
    Order_Count=("Order ID", "nunique"),
    Total_Sales=("Amount", "sum"),
    Total_Profit=("Profit", "sum"),
).reset_index()
city_table["Average Profit Per Order"] = (city_table["Total_Profit"] / city_table["Order_Count"]).round(2)
print("\nCity-level figures for the top 5 states:")
print(city_table.sort_values("Total_Profit").to_string(index=False))


# Question 1, Part 3: Regional Performance Insights
print("\n--- Part 3: Regional Performance ---")

# Top 5 states by order count (each Order ID appears once in the orders table)
top_states = orders["State"].value_counts().head(5).index

# Total sales, total profit and order count for each state (uses 'merged' from Part 1)
state_data = merged[merged["State"].isin(top_states)]
state_table = state_data.groupby("State").agg(
    Order_Count=("Order ID", "nunique"),
    Total_Sales=("Amount", "sum"),
    Total_Profit=("Profit", "sum"),
).reset_index()

# Average profit per order = total profit / number of orders
state_table["Average Profit Per Order"] = (state_table["Total_Profit"] / state_table["Order_Count"]).round(2)
state_table = state_table.sort_values("Order_Count", ascending=False)
print(state_table.to_string(index=False))

# Same figures for each city in the top 5 states
city_table = state_data.groupby(["State", "City"]).agg(
    Order_Count=("Order ID", "nunique"),
    Total_Sales=("Amount", "sum"),
    Total_Profit=("Profit", "sum"),
).reset_index()
city_table["Average Profit Per Order"] = (city_table["Total_Profit"] / city_table["Order_Count"]).round(2)
print("\nCity-level figures for the top 5 states:")
print(city_table.sort_values("Total_Profit").to_string(index=False))