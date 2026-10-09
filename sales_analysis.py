# Question 1, Part A: Sales and Profitability Analysis
# Simple step-by-step script using basic pandas + matplotlib

import pandas as pd
import matplotlib
matplotlib.use("Agg")          # lets charts be saved to files without opening a window
import matplotlib.pyplot as plt

# ---------------------------------------------------------------
# STEP 1: Load the data
# NOTE: the uploaded files are Excel (.xlsx) files, not PDFs,
# so we use pd.read_excel (no PDF table extraction is needed).
# Change the folder below if your files are somewhere else.
# ---------------------------------------------------------------
folder = ""   # e.g. "C:/Users/you/Downloads/" ; leave empty if files are next to this script

orders = pd.read_excel(folder + "List_of_Orders.xlsx")
details = pd.read_excel(folder + "Order_Details.xlsx")

print("Orders shape:", orders.shape)
print("Details shape:", details.shape)

# ---------------------------------------------------------------
# STEP 2: Check column names and data types
# ---------------------------------------------------------------
print("\nOrders columns and types:")
print(orders.dtypes)
print("\nDetails columns and types:")
print(details.dtypes)

# ---------------------------------------------------------------
# STEP 3: Clean the data (missing / invalid values)
# ---------------------------------------------------------------
# Remove extra spaces in text columns
orders["Order ID"] = orders["Order ID"].astype(str).str.strip()
details["Order ID"] = details["Order ID"].astype(str).str.strip()
details["Category"] = details["Category"].astype(str).str.strip()

# Make sure Amount and Profit are numbers (bad values become NaN)
details["Amount"] = pd.to_numeric(details["Amount"], errors="coerce")
details["Profit"] = pd.to_numeric(details["Profit"], errors="coerce")

# Count missing values
print("\nMissing values in details:")
print(details.isna().sum())

# Drop rows where Amount, Profit or Category is missing
rows_before = len(details)
details = details.dropna(subset=["Amount", "Profit", "Category"])
print("Rows dropped because of missing values:", rows_before - len(details))

# Check for duplicate Order IDs in the orders table
# (duplicates here would double-count sales after merging)
duplicate_orders = orders["Order ID"].duplicated().sum()
print("Duplicate Order IDs in orders table:", duplicate_orders)
if duplicate_orders > 0:
    orders = orders.drop_duplicates(subset="Order ID")

# ---------------------------------------------------------------
# STEP 4: Check Order IDs match, then merge
# ---------------------------------------------------------------
unmatched = details[~details["Order ID"].isin(orders["Order ID"])]
print("\nOrder-detail rows with no matching order:", len(unmatched))

# 'left' merge keeps every detail row; each detail row matches one order
merged = details.merge(orders, on="Order ID", how="left")
print("Rows after merge:", len(merged), "(should equal rows in details:", len(details), ")")

# ---------------------------------------------------------------
# STEP 5: Total sales and total profit per category
# Each row of 'merged' is one product line, so summing it does not double count.
# ---------------------------------------------------------------
summary = merged.groupby("Category").agg(
    Total_Sales=("Amount", "sum"),
    Total_Profit=("Profit", "sum"),
).reset_index()

# ---------------------------------------------------------------
# STEP 6: Average profit per order
# Definition: total profit of the category / number of DISTINCT orders
# that contain that category.
# ---------------------------------------------------------------
orders_per_category = merged.groupby("Category")["Order ID"].nunique().reset_index()
orders_per_category.columns = ["Category", "Number_of_Orders"]

summary = summary.merge(orders_per_category, on="Category")
summary["Average_Profit_Per_Order"] = summary["Total_Profit"] / summary["Number_of_Orders"]

# ---------------------------------------------------------------
# STEP 7: Profit margin (%) = Total Profit / Total Sales * 100
# ---------------------------------------------------------------
summary["Profit_Margin_Pct"] = summary["Total_Profit"] / summary["Total_Sales"] * 100

# Round for neat display
summary["Average_Profit_Per_Order"] = summary["Average_Profit_Per_Order"].round(2)
summary["Profit_Margin_Pct"] = summary["Profit_Margin_Pct"].round(2)

# Sort by total sales (highest first)
summary = summary.sort_values("Total_Sales", ascending=False).reset_index(drop=True)

# Final table with the requested column names
final_table = summary[["Category", "Total_Sales", "Total_Profit",
                       "Average_Profit_Per_Order", "Profit_Margin_Pct"]].copy()
final_table.columns = ["Category", "Total Sales", "Total Profit",
                       "Average Profit Per Order", "Profit Margin (%)"]

print("\n===== SUMMARY TABLE =====")
print(final_table.to_string(index=False))
print("\nNumber of distinct orders per category:")
print(summary[["Category", "Number_of_Orders"]].to_string(index=False))

# Sanity check: category totals must equal overall totals
print("\nCheck - sum of category sales:", summary["Total_Sales"].sum(),
      "| sum of Amount column:", details["Amount"].sum())
print("Check - sum of category profit:", summary["Total_Profit"].sum(),
      "| sum of Profit column:", details["Profit"].sum())

# ---------------------------------------------------------------
# STEP 8: Best and worst categories for each measure
# ---------------------------------------------------------------
print("\n===== BEST AND WORST =====")
measures = ["Total Sales", "Average Profit Per Order", "Profit Margin (%)"]
for measure in measures:
    best_row = final_table.loc[final_table[measure].idxmax()]
    worst_row = final_table.loc[final_table[measure].idxmin()]
    print(measure, "-> Best:", best_row["Category"], "(", best_row[measure], ")",
          "| Worst:", worst_row["Category"], "(", worst_row[measure], ")")

# ---------------------------------------------------------------
# STEP 9: Save the table and the charts
# ---------------------------------------------------------------
final_table.to_csv("category_summary.csv", index=False)

# Chart 1: total sales by category
plt.figure(figsize=(6, 4))
plt.bar(final_table["Category"], final_table["Total Sales"], color="steelblue")
plt.title("Total Sales by Category")
plt.xlabel("Category")
plt.ylabel("Total Sales (Amount)")
plt.tight_layout()
plt.savefig("total_sales_by_category.png")
plt.close()

# Chart 2: profit margin by category
plt.figure(figsize=(6, 4))
plt.bar(final_table["Category"], final_table["Profit Margin (%)"], color="seagreen")
plt.title("Profit Margin (%) by Category")
plt.xlabel("Category")
plt.ylabel("Profit Margin (%)")
plt.tight_layout()
plt.savefig("profit_margin_by_category.png")
plt.close()

print("\nSaved: category_summary.csv, total_sales_by_category.png, profit_margin_by_category.png")