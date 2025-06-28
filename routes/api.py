@app.route('/api/error-history')
def get_error_history():
    print(f'Received params: date_from={request.args.get("date_from")}, date_to={request.args.get("date_to")}')