# Question 1, Part A: Sales and Profitability Analysis

import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Load the data (Excel files in the same folder as this script)
orders = pd.read_excel("List of Orders.xlsx")
details = pd.read_excel("Order Details.xlsx")

print("Orders shape:", orders.shape)
print("Details shape:", details.shape)
print("\nOrders columns and types:")
print(orders.dtypes)
print("\nDetails columns and types:")
print(details.dtypes)

# Clean the data
orders["Order ID"] = orders["Order ID"].astype(str).str.strip()
details["Order ID"] = details["Order ID"].astype(str).str.strip()
details["Category"] = details["Category"].astype(str).str.strip()
details["Amount"] = pd.to_numeric(details["Amount"], errors="coerce")
details["Profit"] = pd.to_numeric(details["Profit"], errors="coerce")

print("\nMissing values in details:")
print(details.isna().sum())

rows_before = len(details)
details = details.dropna(subset=["Amount", "Profit", "Category"])
print("Rows dropped because of missing values:", rows_before - len(details))

duplicate_orders = orders["Order ID"].duplicated().sum()
print("Duplicate Order IDs in orders table:", duplicate_orders)
if duplicate_orders > 0:
    orders = orders.drop_duplicates(subset="Order ID")

# Check for unmatched rows, then merge on Order ID
unmatched = details[~details["Order ID"].isin(orders["Order ID"])]
print("\nOrder-detail rows with no matching order:", len(unmatched))

merged = details.merge(orders, on="Order ID", how="left")
print("Rows after merge:", len(merged), "(should equal rows in details:", len(details), ")")

# Total sales and total profit per category
summary = merged.groupby("Category").agg(
    Total_Sales=("Amount", "sum"),
    Total_Profit=("Profit", "sum"),
).reset_index()

# Average profit per order = total profit / number of distinct orders in the category
orders_per_category = merged.groupby("Category")["Order ID"].nunique().reset_index()
orders_per_category.columns = ["Category", "Number_of_Orders"]
summary = summary.merge(orders_per_category, on="Category")
summary["Average_Profit_Per_Order"] = summary["Total_Profit"] / summary["Number_of_Orders"]

# Profit margin (%) = total profit / total sales * 100
summary["Profit_Margin_Pct"] = summary["Total_Profit"] / summary["Total_Sales"] * 100

summary["Average_Profit_Per_Order"] = summary["Average_Profit_Per_Order"].round(2)
summary["Profit_Margin_Pct"] = summary["Profit_Margin_Pct"].round(2)
summary = summary.sort_values("Total_Sales", ascending=False).reset_index(drop=True)

final_table = summary[["Category", "Total_Sales", "Total_Profit",
                       "Average_Profit_Per_Order", "Profit_Margin_Pct"]].copy()
final_table.columns = ["Category", "Total Sales", "Total Profit",
                       "Average Profit Per Order", "Profit Margin (%)"]

print("\n [SUMMARY TABLE] ")
print(final_table.to_string(index=False))
print("\nNumber of distinct orders per category:")
print(summary[["Category", "Number_of_Orders"]].to_string(index=False))

# Check: category totals should equal overall totals
print("\nCheck - sum of category sales:", summary["Total_Sales"].sum(),
      "| sum of Amount column:", details["Amount"].sum())
print("Check - sum of category profit:", summary["Total_Profit"].sum(),
      "| sum of Profit column:", details["Profit"].sum())

# Best and worst categories
print("\n [BEST AND WORST] ")
for measure in ["Total Sales", "Average Profit Per Order", "Profit Margin (%)"]:
    best_row = final_table.loc[final_table[measure].idxmax()]
    worst_row = final_table.loc[final_table[measure].idxmin()]
    print(measure, "-> Best:", best_row["Category"], "(", best_row[measure], ")",
          "| Worst:", worst_row["Category"], "(", worst_row[measure], ")")

# Save the table and charts
final_table.to_csv("category_summary.csv", index=False)

plt.figure(figsize=(6, 4))
plt.bar(final_table["Category"], final_table["Total Sales"], color="steelblue")
plt.title("Total Sales by Category")
plt.xlabel("Category")
plt.ylabel("Total Sales (Amount)")
plt.tight_layout()
plt.savefig("total_sales_by_category.png")
plt.close()

plt.figure(figsize=(6, 4))
plt.bar(final_table["Category"], final_table["Profit Margin (%)"], color="seagreen")
plt.title("Profit Margin (%) by Category")
plt.xlabel("Category")
plt.ylabel("Profit Margin (%)")
plt.tight_layout()
plt.savefig("profit_margin_by_category.png")
plt.close()

print("\nSaved: category_summary.csv, total_sales_by_category.png, profit_margin_by_category.png")