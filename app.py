from flask import Flask, render_template, request
from datetime import datetime
import database  # твой модуль с функциями БД

app = Flask(__name__)

@app.route("/")
def home():
    genres = database.get_all_genres()
    current_year = datetime.now().year
    top_films = database.get_top_violent_films()  # топ 10 по жестокости
    top_queries = database.get_popular_queries()  # возвращаем топ поисков

    return render_template("index.html", genres=genres, current_year=current_year,
                           top_films=top_films, top_queries=top_queries)



@app.route("/search", methods=["POST"])
def search():
    keyword = request.form.get("keyword", "").strip().replace(',', '')
    selected_genres = request.form.getlist("genres[]")
    year_from = request.form.get("year_from", type=int)
    year_to = request.form.get("year_to", type=int)
    sort_by = request.form.get("sort", "title_asc")

    results = database.advanced_search(keyword, selected_genres, year_from, year_to, sort_by)

    # логируем, только если keyword точно совпадает с названием фильма
    if keyword.strip() and results:
        database.log_search(keyword.strip(), "keyword")


    return render_template("results.html", films=results)



@app.route("/popular")
def popular():
    top_queries = database.get_popular_queries()
    return render_template("popular.html", queries=top_queries)

if __name__ == "__main__":
    app.run(debug=True)
