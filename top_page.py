from flask import render_template


def top_page(index):
    if index in range(1, 5):
        return render_template(f"top_page{index}.html")
    else:
        return "Invalid index"
