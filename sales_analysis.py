# ==============================================================================
# JAR GROWTH INTERN ASSIGNMENT - QUESTION 1, PART A: SALES & PROFITABILITY ANALYSIS
# ==============================================================================

import pandas as pd
import pdfplumber
import matplotlib.pyplot as plt

# ------------------------------------------------------------------------------
# STEP 1: Load Datasets from PDF Files
# ------------------------------------------------------------------------------
# Function to extract tabular data from a PDF file using pdfplumber
def load_pdf_table(pdf_filepath):
    table_rows = []
    header_columns = None
    
    with pdfplumber.open(pdf_filepath) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                for row in table:
                    # Skip empty rows
                    if not row or all(cell is None or cell == '' for cell in row):
                        continue
                    # Set the first non-empty row as headers
                    if header_columns is None:
                        header_columns = [col.strip() for col in row if col and col.strip() != '']
                    else:
                        # Skip repeated header rows across PDF pages
                        if [c.strip() for c in row if c and c.strip() != ''] == header_columns:
                            continue
                        table_rows.append(row[:len(header_columns)])
                        
    # Create DataFrame and clean column names
    df = pd.DataFrame(table_rows, columns=header_columns)
    return df

print("Loading 'List of Orders.pdf' and 'Order Details.pdf'...")
df_orders = load_pdf_table("List_of_Orders.pdf")
df_details = load_pdf_table("Order_Details.pdf")

print(f"List of Orders loaded: {len(df_orders)} rows")
print(f"Order Details loaded: {len(df_details)} rows")

# ------------------------------------------------------------------------------
# STEP 2: Data Cleaning and Type Conversion
# ------------------------------------------------------------------------------
# Convert numeric columns in Order Details to proper numeric data types
df_details['Amount'] = pd.to_numeric(df_details['Amount'], errors='coerce')
df_details['Profit'] = pd.to_numeric(df_details['Profit'], errors='coerce')
df_details['Quantity'] = pd.to_numeric(df_details['Quantity'], errors='coerce')

# Drop any rows with missing essential values
df_details = df_details.dropna(subset=['Order ID', 'Amount', 'Profit', 'Category'])

# ------------------------------------------------------------------------------
# STEP 3: Merge Datasets and Check for Unmatched Rows
# ------------------------------------------------------------------------------
# Merge Order Details with List of Orders on 'Order ID'
merged_df = pd.merge(df_details, df_orders, on='Order ID', how='left', indicator=True)

# Check if any order detail rows failed to match an order
unmatched_count = (merged_df['_merge'] != 'both').sum()
print(f"\nUnmatched order detail rows: {unmatched_count}")

# ------------------------------------------------------------------------------
# STEP 4: Calculate Category Sales and Profitability Metrics
# ------------------------------------------------------------------------------
# Group by Category and calculate metrics
# Definition:
# - Total Sales = sum of 'Amount' for each category
# - Total Profit = sum of 'Profit' for each category
# - Distinct Orders = count of unique 'Order ID's containing items from each category
# - Average Profit Per Order = Total Profit / Distinct Orders
# - Profit Margin (%) = (Total Profit / Total Sales) * 100

category_summary = df_details.groupby('Category').agg(
    Total_Sales=('Amount', 'sum'),
    Total_Profit=('Profit', 'sum'),
    Distinct_Orders=('Order ID', 'nunique')
).reset_index()

# Calculate Average Profit Per Order and Profit Margin (%)
category_summary['Average Profit Per Order'] = category_summary['Total_Profit'] / category_summary['Distinct_Orders']
category_summary['Profit Margin (%)'] = (category_summary['Total_Profit'] / category_summary['Total_Sales']) * 100

# Format column names for presentation
summary_table = category_summary.rename(columns={
    'Total_Sales': 'Total Sales',
    'Total_Profit': 'Total Profit'
})

print("\n=================== SALES & PROFITABILITY SUMMARY ===================")
print(summary_table.to_string(index=False))

# Save summary table to CSV
summary_table.to_csv("sales_profitability_summary.csv", index=False)
print("\nSummary saved to 'sales_profitability_summary.csv'")

# ------------------------------------------------------------------------------
# STEP 5: Generate Charts
# ------------------------------------------------------------------------------
# Chart 1: Total Sales by Category
plt.figure(figsize=(7, 4.5))
plt.bar(summary_table['Category'], summary_table['Total Sales'], color=['#3498db', '#2ecc71', '#e74c3c'])
plt.title('Total Sales by Category')
plt.xlabel('Category')
plt.ylabel('Total Sales (INR)')
for i, v in enumerate(summary_table['Total Sales']):
    plt.text(i, v + 2000, f"INR {v:,.0f}", ha='center', fontweight='bold')
plt.tight_layout()
plt.savefig('total_sales_by_category.png', dpi=300)
plt.close()

# Chart 2: Profit Margin (%) by Category
plt.figure(figsize=(7, 4.5))
plt.bar(summary_table['Category'], summary_table['Profit Margin (%)'], color=['#3498db', '#2ecc71', '#e74c3c'])
plt.title('Profit Margin (%) by Category')
plt.xlabel('Category')
plt.ylabel('Profit Margin (%)')
for i, v in enumerate(summary_table['Profit Margin (%)']):
    plt.text(i, v + 0.2, f"{v:.2f}%", ha='center', fontweight='bold')
plt.tight_layout()
plt.savefig('profit_margin_by_category.png', dpi=300)
plt.close()

print("Charts saved: 'total_sales_by_category.png' and 'profit_margin_by_category.png'")
