import pandas as pd
import numpy as np
import copy
import pizza_analysis_cleaning as pac


def create_excel(optimal_ingredients, df_orders, df_order_details, df_categories,
                 df_subcategories, df_weekly_pizzas_total, df_profits):
    """
    Create an Excel writer to generate more than one sheet in the same
    Excel file. This sheets will contain information about optimal
    ingredients, orders and order details.
    """
    writer = pd.ExcelWriter("report.xlsx", engine="xlsxwriter")

    # We start generating the ingredients DataFrame
    ingredients = {"Ingredients": [], "Quantity": []}
    for key, value in optimal_ingredients.items():
        ingredients["Ingredients"].append(key)
        ingredients["Quantity"].append(value)
    df = pd.DataFrame(ingredients)

    # Now we export them to excel files
    df.to_excel(writer, sheet_name="optimal_ingredients", index=False)
    df_orders.to_excel(writer, sheet_name="orders", index=False)
    df_order_details.to_excel(writer, sheet_name="order_details", index=False)

    # We also report the executive report DataFrames
    df_categories.to_excel(writer, sheet_name="executive_report", index=False,
                           startrow=0, startcol=0)
    df_subcategories.to_excel(writer, sheet_name="executive_report", index=False,
                              startrow=0, startcol=3)
    df_weekly_pizzas_total.to_excel(writer, sheet_name="executive_report", index=False,
                                    startrow=0, startcol=6)
    df_profits.to_excel(writer, sheet_name="executive_report", index=False,
                        startrow=0, startcol=9)

    # Let's add some graphs
    workbook = writer.book
    worksheet = writer.sheets["executive_report"]
    chart1 = workbook.add_chart({"type": "pie"})
    chart1.add_series({
        "categories": ["executive_report", 1, 0, 4, 0],
        "values": ["executive_report", 1, 1, 4, 1],
        "gap": 2,
        "name": "Total Orders by Category"
    })
    worksheet.insert_chart("M2", chart1, {"x_scale": 2, "y_sacale": 0.75})

    chart2 = workbook.add_chart({"type": "column"})
    chart2.add_series({
        "categories": ["executive_report", 1, 3, 32, 3],
        "values": ["executive_report", 1, 4, 32, 4],
        "gap": 200,
        "name": "Total Orders by Subcategory"
    })
    chart2.set_x_axis({
        "name": "Subcategory",
        "name_font": {"size": 14}
    })
    worksheet.insert_chart("M19", chart2, {"x_scale": 2, "y_sacale": 0.75})

    chart3 = workbook.add_chart({"type": "line"})
    chart3.add_series({
        "categories": ["executive_report", 1, 6, 26, 6],
        "values": ["executive_report", 1, 7, 26, 7],
        "gap": 200,
        "name": "Orders by Week of the Year",
        "marker": {"type": "automatic"},
        "line": {"width": 3.25}
    })
    worksheet.insert_chart("M36", chart3, {"x_scale": 2, "y_sacale": 0.75})

    chart4 = workbook.add_chart({"type": "line"})
    chart4.add_series({
        "categories": ["executive_report", 1, 9, 50, 9],
        "values": ["executive_report", 1, 10, 50, 10],
        "gap": 200,
        "name": "Profits by Week of the Year",
        "marker": {"type": "automatic"},
        "line": {"width": 3.25,
                 "color": "#FF9900"}
    })
    worksheet.insert_chart("M56", chart4, {"x_scale": 2, "y_sacale": 0.75})

    writer.save()
    return None


def create_profits(df_weekly_pizzas, df_prices):
    weeks = [i for i in range(1, 51)]
    profits = []

    for i in range(1, 51):
        profit = 0
        for j in range(df_weekly_pizzas.shape[0]):
            pizza = df_weekly_pizzas.iloc[j, 0]
            price = df_prices.loc[pizza, "price"]
            sold = df_weekly_pizzas.iloc[j, i]
            if sold >= df_weekly_pizzas.loc[j, "optimal"]:
                profit += (df_weekly_pizzas.loc[j, "optimal"] * price * 0.15)  # We add the profit for each pizza sold.
            else:
                remaining = df_weekly_pizzas.loc[j, "optimal"] - sold
                profit -= (remaining * price * 0.85)
        profits.append(profit)

    profits_dict = {"week": weeks,
                    "profit": profits}
    df_profits = pd.DataFrame(profits_dict)
    return df_profits


def create_weekly_pizzas_total(df_weekly_pizzas):
    weekly_pizzas_total = {"weeks": [], "orders": []}
    week = 1
    for column in df_weekly_pizzas.columns:
        if column not in ["pizza", "mean", "optimal"]:
            if week % 2 == 1:
                weekly_pizzas_total["weeks"].append(week)
                weekly_pizzas_total["orders"].append(df_weekly_pizzas[column].sum())
            week += 1

    df_weekly_pizzas_total = pd.DataFrame(weekly_pizzas_total)
    return df_weekly_pizzas_total


def update_order_details(df_order_details, df_pizza_types):
    df_order_details.dropna()
    new_df = copy.deepcopy(df_order_details)
    new_df["category"] = ""
    new_df["subcategory"] = ""
    for i in range(new_df.shape[0]):
        pizza = new_df.iloc[i, 2]
        if pizza[-2] != "_":
            # We check this beacuse the greek pizza can be xl or xxl.
            pizza = pizza[:9]
        else:
            pizza = pizza[:-2]
        new_df.loc[i, "subcategory"] = pizza
        j = 0
        found = False
        while not found and j < df_pizza_types.shape[0]:
            if df_pizza_types.iloc[j, 0] == pizza:
                new_df.loc[i, "category"] = df_pizza_types.iloc[j, 2]
                found = True
            j += 1
    return new_df


def create_cat_subcat(df_order_details):
    total = df_order_details.shape[0] - 1
    categories = sorted(list(df_order_details["category"].unique()))
    categories.remove("")
    counts = [i for i in df_order_details["category"].value_counts().sort_index()]
    counts.remove(1)

    subcategories = sorted(list(df_order_details["subcategory"].unique()))
    subcategories.remove("")
    counts_sub = [i for i in df_order_details["subcategory"].value_counts().sort_index()]
    counts_sub.remove(1)

    new_counts_sub = [round(count / total * 100, 2) for count in counts_sub]

    dict_categories = {"categories": categories,
                       "counts": counts}
    df_categories = pd.DataFrame(dict_categories)

    dict_subcategories = {"subcategories": subcategories,
                        "percentage": new_counts_sub}
    df_subcategories = pd.DataFrame(dict_subcategories)
    df_subcategories = df_subcategories.sort_values("percentage", ascending=True)

    return df_categories, df_subcategories


if __name__ == "__main__":
    df_order_details = pd.read_csv("order_details.csv", sep=";", encoding="latin1")
    df_orders = pd.read_csv("orders.csv", sep=";")
    df_pizzas = pd.read_csv("pizzas.csv")
    df_pizza_types = pd.read_csv("pizza_types.csv", encoding="latin1")

    df_orders = df_orders.sort_values("order_id")
    df_orders = df_orders.reset_index(drop=True)
    df_orders.index = np.arange(1, len(df_orders) + 1)
    df_order_details = df_order_details.sort_values("order_details_id")
    df_order_details = df_order_details.reset_index(drop=True)
    df_order_details.index = np.arange(1, len(df_order_details) + 1)

    pizza_ingredients = pac.create_pizza_ingredients(df_pizza_types)
    ingredients = pac.create_ingredients(pizza_ingredients)

    df_prices = pac.obtain_prices(df_pizzas)
    df_orders = pac.clean_orders(df_orders)
    df_order_details = pac.clean_order_details(pizza_ingredients, df_order_details)
    df_weekly_pizzas = pac.create_weekly_pizzas(df_orders, df_order_details, df_prices, pizza_ingredients)

    optimal_ingredients = pac.obtain_optimal(df_weekly_pizzas, pizza_ingredients, ingredients)

    df_weekly_pizzas_total = create_weekly_pizzas_total(df_weekly_pizzas)
    df_profits = create_profits(df_weekly_pizzas, df_prices)
    df_order_details = update_order_details(df_order_details, df_pizza_types)
    df_categories, df_subcategories = create_cat_subcat(df_order_details)

    create_excel(optimal_ingredients, df_orders, df_order_details, df_categories,
                 df_subcategories, df_weekly_pizzas_total, df_profits)
