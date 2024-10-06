from flask import Flask, jsonify, request
from flask_cors import CORS
from piechart import calculate_spending
from piechart import getTxCount
from piechart import category_with_most_spending
from piechart import most_recurring_transaction
from piechart import total_spent
from piechart import total_income
from piechart import get_six_most_expensive_days
from piechart import get_three_most_expensive_transactions
from piechart import getAiTips
import os
import pandas as pd
#app instance
app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload directory exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/upload_csv', methods=['POST'])
def upload_csv():
    global global_df
    try:
        # Check if the request has a file part
        if 'file' not in request.files:
            return jsonify({"error": "No file part in the request"}), 400

        file = request.files['file']

        # If no file is selected
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400

        # Ensure the file is a CSV
        if file and file.filename.endswith('.csv'):
            # Clear existing files in the uploads folder
            for filename in os.listdir(app.config['UPLOAD_FOLDER']):
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)

            # Save the new file
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)

            # Load the CSV into a DataFrame and assign it to global_df
            global_df = pd.read_csv(file_path)


            # Example: Return the first few rows of the CSV
            return jsonify({"message": global_df.head().to_dict()}), 200
        else:
            return jsonify({"error": "File must be a CSV"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Example data - you can replace this with database calls

@app.route("/api/chart", methods=['GET'])
def return_chart():

    result = calculate_spending(global_df)

    return jsonify({
        'message':result
    })

@app.route("/api/bar", methods=['GET'])
def return_bar():

    result = getTxCount(global_df)

    return jsonify({
        'message':result
    })


@app.route("/api/bottoml", methods=['GET'])
def return_bottomL():

    category, amount = category_with_most_spending(global_df)
    transaction, count = most_recurring_transaction(global_df)
    amount = int(amount)  # Convert from int64 to int
    count = int(count)
    income = total_income(global_df)
    spent = total_spent(global_df)
    spent = int(spent)
    income = int(income)

    return jsonify({
        "message": {
            "SpentCat": {
                "category": category,
                "amount": amount
            },
            "mostTX": {
                "transaction": transaction,
                "count": count
            },
            "totalSpent" : spent,
            "totalIncome" : income
        }
    })

@app.route("/api/bottomm", methods=['GET'])
def return_bottomLM():

    mostExpensive = get_three_most_expensive_transactions(global_df)
    mostExpensiveDay = get_six_most_expensive_days(global_df)

    return jsonify({
        "message": {
            "days" : mostExpensiveDay,
            "tx" : mostExpensive
        }
    })

@app.route("/api/aitips", methods=['GET'])
def return_aitips():

    transaction_summary = calculate_spending(global_df)
    transaction_summary['most_recurring_tx'], transaction_summary['most_recurring_tx_count'] = most_recurring_transaction(global_df)
    response = getAiTips(transaction_summary)
    responseTwo = getAiTips(transaction_summary)

    return jsonify({
        "message": {
            "response" : response,
            "responseTwo" : responseTwo
        }
    })





if __name__ == '__main__':
    app.run(debug=True, port=8080)