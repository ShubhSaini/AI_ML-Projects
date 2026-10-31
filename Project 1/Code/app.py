# TMDB Movie Explorer - run with:  streamlit run app.py
import mysql.connector
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Movie Analytics", page_icon="🎬", layout="wide")
st.title("🎬 Movie Analytics")


# ---------- Database ----------
@st.cache_data
def run_query(sql, ):
    conn = mysql.connector.connect(host="localhost", user="root",
                                   password="Assasin#96", database="project_1")
    cursor = conn.cursor()
    cursor.execute(sql)
    df = pd.DataFrame(cursor.fetchall(), columns=cursor.column_names)
    conn.close()
    return df


movies = run_query("SELECT movie_id, title, original_language, release_date, budget, revenue, vote_average FROM movies")
movies["release_year"] = pd.to_datetime(movies["release_date"]).dt.year
genres = run_query("SELECT * FROM genres")
movie_genres = run_query("SELECT * FROM movie_genres")
cast = run_query("SELECT movie_id, person_id FROM cast")

# ---------- Sidebar: page choice + filters (the widget keys store the values in st.session_state) ----------

st.sidebar.header("Shared Filters")
year_min, year_max = int(movies["release_year"].min()), int(movies["release_year"].max())
st.sidebar.multiselect("Genre (empty = all)", sorted(genres["genre_name"]), key="genres")
st.sidebar.slider("Release year", year_min, year_max, (year_min, year_max), key="years")
st.sidebar.slider("Minimum rating", 0.0, 10.0, 0.0, 0.1, key="rating")
st.sidebar.selectbox("Language", ["All"] + sorted(movies["original_language"].unique()), key="language")

# Apply the saved filter values
df = movies[movies["release_year"].between(*st.session_state["years"])]
df = df[df["vote_average"] >= st.session_state["rating"]]
if st.session_state["language"] != "All":
    df = df[df["original_language"] == st.session_state["language"]]
if st.session_state["genres"]:
    chosen_ids = genres[genres["genre_name"].isin(st.session_state["genres"])]["genre_id"]
    movie_ids = movie_genres[movie_genres["genre_id"].isin(chosen_ids)]["movie_id"]
    df = df[df["movie_id"].isin(movie_ids)]

st.sidebar.metric("Movies matching the filters", len(df))   # live count

if df.empty:
    st.warning("No movies match the current filters.")
    st.stop()

# ---------- Page: Filters ----------
def filter_page():
    st.title("Filters")
    st.caption("Review the filters selected in the sidebar and the movies matching them.")

    # Display selected filters
    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Selected genres", len(st.session_state["genres"]))
    c2.metric("Minimum rating", st.session_state["rating"])
    c3.metric("Start year", st.session_state["years"][0])
    c4.metric("End year", st.session_state["years"][1])

    st.write("**Selected language:**", st.session_state["language"])

    if st.session_state["genres"]:
        st.write("**Selected genres:**", ", ".join(st.session_state["genres"]))
    else:
        st.write("**Selected genres:** All")

    # Display matching movie count
    st.subheader("Matching Movies")
    st.metric("Total movies matching filters", len(df))

    # Display filtered movie records
    st.subheader("Filtered Movie Details")

    st.dataframe(
        df[[
            "movie_id",
            "title",
            "original_language",
            "release_year",
            "budget",
            "revenue",
            "vote_average"
        ]],
        width="stretch",
        hide_index=True
    )

# ---------- Page: Dashboard ----------
def dashboard_page():
    st.title("Dashboard")
    st.caption("All KPIs and charts use the shared sidebar filters.")
    genre_rows = movie_genres[movie_genres["movie_id"].isin(df["movie_id"])].merge(genres, on="genre_id")
    actors = cast[cast["movie_id"].isin(df["movie_id"])]["person_id"].nunique()

    # KPI cards
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total movies", len(df))
    c2.metric("Genres represented", genre_rows["genre_id"].nunique())
    c3.metric("Total actors", actors)
    c4.metric("Average rating", round(df["vote_average"].mean(), 2))

    # Top 10 movies by revenue
    top10 = df.nlargest(10, "revenue")
    st.plotly_chart(px.bar(top10, x="revenue", y="title", orientation="h", title="Top 10 movies by revenue")
                    .update_layout(yaxis={"categoryorder": "total ascending"}), width="stretch")

    # Genre distribution
    genre_counts = genre_rows["genre_name"].value_counts().reset_index()
    st.plotly_chart(px.bar(genre_counts, x="genre_name", y="count", title="Movies per genre"), width="stretch")

    # Budget vs revenue (0 means unknown, so those movies are left out)
    known = df[(df["budget"] > 0) & (df["revenue"] > 0)]
    st.plotly_chart(px.scatter(known, x="budget", y="revenue", hover_name="title", log_x=True, log_y=True,
                               title="Budget vs revenue"), width="stretch")

    # Text insight
    revenue_by_genre = genre_rows.merge(df[["movie_id", "revenue"]], on="movie_id").groupby("genre_name")["revenue"].sum()
    st.info(f"In this selection of {len(df)} movies, the highest-grossing genre is {revenue_by_genre.idxmax()} "
            f"and the top movie is {top10.iloc[0]['title']}.")

# ---------- Page: Query Explorer (each query only looks at the filtered movies) ----------
def query_explorer_page():
    st.title("Query Explorer")
    st.write("Select a saved analysis. Results are filtered using the same sidebar selections.")
    QUERIES = {
        "Top 10 highest-grossing movies":
            "SELECT title, revenue FROM movies WHERE movie_id IN {ids} ORDER BY revenue DESC LIMIT 10",
        "Top 10 actors by number of movies":
            "SELECT actor_name, COUNT(DISTINCT movie_id) AS movies FROM cast WHERE movie_id IN {ids} "
            "GROUP BY person_id, actor_name ORDER BY movies DESC LIMIT 10",
        "Top 10 keywords":
            "SELECT keyword_name, COUNT(DISTINCT movie_id) AS movies FROM movie_keywords WHERE movie_id IN {ids} "
            "GROUP BY keyword_id, keyword_name ORDER BY movies DESC LIMIT 10",
        "Average rating by genre (genres with at least 20 movies)":
            "SELECT g.genre_name, ROUND(AVG(m.vote_average), 2) AS avg_rating FROM movies m "
            "JOIN movie_genres mg ON m.movie_id = mg.movie_id JOIN genres g ON mg.genre_id = g.genre_id "
            "WHERE m.movie_id IN {ids} GROUP BY g.genre_name HAVING COUNT(*) >= 20 ORDER BY avg_rating DESC",
        "Top 10 movies by number of keywords":
            "SELECT m.title, COUNT(DISTINCT mk.keyword_id) AS keywords FROM movies m "
            "JOIN movie_keywords mk ON m.movie_id = mk.movie_id WHERE m.movie_id IN {ids} "
            "GROUP BY m.movie_id, m.title ORDER BY keywords DESC LIMIT 10",
    }

    name = st.selectbox("Saved query", list(QUERIES))
    ids = "(" + ",".join(str(i) for i in df["movie_id"]) + ")"      # the filtered movie ids, as SQL text
    result = run_query(QUERIES[name].format(ids=ids))

    if result.empty:
        st.info("This query returns no rows for the current filters.")
    else:
        st.dataframe(result, width="stretch")
        st.plotly_chart(px.bar(result, x=result.columns[1], y=result.columns[0], orientation="h")
                        .update_layout(yaxis={"categoryorder": "total ascending"}), width="stretch")
        st.info(f"The top result is {result.iloc[0, 0]} ({result.columns[1]}: {result.iloc[0, 1]}).")

pages = [st.Page(filter_page, title="Filters", icon="🔎"),
    st.Page(dashboard_page, title="Dashboard", icon="📊"),
    st.Page(query_explorer_page, title="Query Explorer", icon="🧭"),
]
st.navigation(pages).run()