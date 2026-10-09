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