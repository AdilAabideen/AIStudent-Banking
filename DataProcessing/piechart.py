import pandas as pd
from openai import OpenAI
from dotenv import load_dotenv
import os
import matplotlib.pyplot as plt
import time

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))  # Import openai, not OpenAI

def categorizeTX(tx):
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "Please Can you categorize this transaction for me. Return only category name. Categories: Food, Transfers, Enjoyment, Bills, Clothes, Travel, Other."},
            {"role": "user", "content": "RETURN ONLY CATEGORY: " + tx}
        ],
        model="gpt-4o-mini",
        temperature=1,
        max_tokens=68
    )
    return chat_completion.choices[0].message.content

def dfCounter(global_df):
    food_list = []
    clothes_list = []
    enjoyment_list = []
    transfers_list = []
    bills_list = []
    travel_list = []
    other_list = []
    income_list = []

    for index, row in global_df.iterrows():
        if pd.notna(row['Paidout']):
            category = categorizeTX(f"Description: {row['Paymenttypeanddetails']}, Paid Out: {row['Paidout']}")
            if "Food" in category:
                food_list.append(row)
            elif "Clothes" in category:
                clothes_list.append(row)
            elif "Enjoyment" in category:
                enjoyment_list.append(row)
            elif "Transfer" in category:
                transfers_list.append(row)
            elif "Bills" in category:
                bills_list.append(row)
            elif "Travel" in category:
                travel_list.append(row)
            else:
                other_list.append(row)
        elif pd.notna(row['Paidin']):
            income_list.append(row)

    food_df = pd.DataFrame(food_list)
    clothes_df = pd.DataFrame(clothes_list)
    enjoyment_df = pd.DataFrame(enjoyment_list)
    transfers_df = pd.DataFrame(transfers_list)
    bills_df = pd.DataFrame(bills_list)
    travel_df = pd.DataFrame(travel_list)
    other_df = pd.DataFrame(other_list)
    income_df = pd.DataFrame(income_list)

    return {
        'food_df': food_df,
        'clothes_df': clothes_df,
        'enjoyment_df': enjoyment_df,
        'transfers_df': transfers_df,
        'bills_df': bills_df,
        'travel_df': travel_df,
        'other_df': other_df,
        'income_df': income_df
    }

def calculate_spending(global_df):
    dfS = dfCounter(global_df)

    def calculate_total_spending(df):
        return df['Paidout'].sum() if not df.empty else 0

    total_spent_food = calculate_total_spending(dfS['food_df'])
    total_spent_clothes = calculate_total_spending(dfS['clothes_df'])
    total_spent_enjoyment = calculate_total_spending(dfS['enjoyment_df'])
    total_spent_transfers = calculate_total_spending(dfS['transfers_df'])
    total_spent_bills = calculate_total_spending(dfS['bills_df'])
    total_spent_travel = calculate_total_spending(dfS['travel_df'])
    total_spent_other = calculate_total_spending(dfS['other_df'])

    category_spending = {
        'Food': total_spent_food,
        'Clothes': total_spent_clothes,
        'Enjoyment': total_spent_enjoyment,
        'Transfers': total_spent_transfers,
        'Bills': total_spent_bills,
        'Travel': total_spent_travel,
        'Other': total_spent_other
    }

    return category_spending

def getTxCount(global_df):
    dfS = dfCounter(global_df)
    return {
        "Food": len(dfS['food_df']),
        "Clothes": len(dfS['clothes_df']),
        "Enjoyment": len(dfS['enjoyment_df']),
        "Transfers": len(dfS['transfers_df']),
        "Bills": len(dfS['bills_df']),
        "Travel": len(dfS['travel_df']),
        "Other": len(dfS['other_df']),
        "Income": len(dfS['income_df'])
    }

def category_with_most_spending(global_df):
    category_spending = calculate_spending(global_df)
    max_category = max(category_spending, key=category_spending.get)
    max_spending = category_spending[max_category]
    return max_category, max_spending

def most_recurring_transaction(global_df):
    dfS = dfCounter(global_df)
    all_transactions = pd.concat([dfS['food_df'], dfS['clothes_df'], dfS['enjoyment_df'], dfS['transfers_df'], dfS['bills_df'], dfS['travel_df'], dfS['other_df'], dfS['income_df']])
    most_recurring_tx = all_transactions['Paymenttypeanddetails'].value_counts().idxmax()
    tx_count = all_transactions['Paymenttypeanddetails'].value_counts().max()
    return most_recurring_tx, tx_count

def total_spent(global_df):
    category_spending = calculate_spending(global_df)
    total = sum(category_spending.values())
    return total

def total_income(global_df):
    dfS = dfCounter(global_df)
    total = dfS['income_df']['Paidin'].sum() if not dfS['income_df'].empty else 0
    return total

def get_three_most_expensive_transactions(global_df):
    dfS = dfCounter(global_df)
    all_paidout_transactions = pd.concat([dfS['food_df'], dfS['clothes_df'], dfS['enjoyment_df'], dfS['transfers_df'], dfS['bills_df'], dfS['travel_df'], dfS['other_df']])
    most_expensive_transactions = all_paidout_transactions.nlargest(3, 'Paidout')
    result = [
        {"transaction": row['Paymenttypeanddetails'], "amount": row['Paidout']}
        for _, row in most_expensive_transactions.iterrows()
    ]
    return result

def get_six_most_expensive_days(global_df):
    dfS = dfCounter(global_df)
    all_paidout_transactions = pd.concat([dfS['food_df'], dfS['clothes_df'], dfS['enjoyment_df'], dfS['transfers_df'], dfS['bills_df'], dfS['travel_df'], dfS['other_df']])
    all_paidout_transactions['Date'] = pd.to_datetime(all_paidout_transactions['Date'], errors='coerce')
    total_spent_per_day = all_paidout_transactions.groupby('Date')['Paidout'].sum()
    most_expensive_days = total_spent_per_day.nlargest(6)
    result = [
        {"date": day.strftime('%a %d %b'), "total_spent": amount}
        for day, amount in most_expensive_days.items()
    ]
    return result



def getAiTips(transaction_summary):
    prompt = f"""
    I have the following transaction summary:

    - Food: ${transaction_summary['Food']}
    - Clothes: ${transaction_summary['Clothes']}
    - Enjoyment: ${transaction_summary['Enjoyment']}
    - Transfers: ${transaction_summary['Transfers']}
    - Bills: ${transaction_summary['Bills']}
    - Travel: ${transaction_summary['Travel']}
    - Other: ${transaction_summary['Other']}
    - Recurring Transactions: {transaction_summary['most_recurring_tx']} (recurring {transaction_summary['most_recurring_tx_count']} times)

    Based on this, can you provide personalized financial advice on how I can improve my spending, save money, or invest smarter?
    """

    chat_completion = client.chat.completions.create(
    messages=[
        {"role" : "system" , "content" : "Please can you give me a personalised financial response on this data  "},
        {"role" : 'user', "content" : prompt }
    ],
    model="gpt-4o-mini",
    temperature=1,
    max_tokens=68
    )

    return chat_completion.choices[0].message.content