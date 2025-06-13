# utils/charts.py

def generate_pnl_chart(pnl_list: list) -> str:
    if not pnl_list:
        return "No data 📭"

    chart = ""
    for value in pnl_list:
        if value > 0:
            chart += "🟩"
        elif value < 0:
            chart += "🟥"
        else:
            chart += "⬜️"
    return chart
