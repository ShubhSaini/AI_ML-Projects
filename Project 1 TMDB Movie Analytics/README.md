# TMDB Movies: SQL, Pandas and Streamlit Analysis

An end-to-end data analysis project on about 2,500 movies from The Movie Database (TMDB). Six raw CSV files are cleaned in Python, stored in a MySQL database, analysed with SQL and Pandas, visualised, and presented in a multi-page Streamlit app.

---

## 1. Project overview and objectives

**Problem:** Load and clean six relational CSV files (movies, genres, movie_genres, cast, crew, movie_keywords), structure them as a proper relational database, and run a full analysis pipeline.

**Objectives**

1. Load, inspect and clean the six tables (placeholders, data types, duplicates, orphaned rows).
2. Build a relational MySQL database (`project_1`) with primary and foreign keys.
3. Answer 10 business questions with SQL (JOIN, GROUP BY, HAVING, subqueries).
4. Answer 10 analysis questions with Pandas, each followed by a short insight.
5. Produce 12 univariate, bivariate and multivariate visualisations, each with an insight.
6. Deliver a multi-page Streamlit app (Filters, Dashboard, Query Explorer) that reads from the database.

---

## 2. Tools and technologies

| Area | Tools |
|---|---|
| Language | Python 3 |
| Data handling | pandas, NumPy |
| Database | MySQL 8, MySQL Workbench, `mysql-connector-python` |
| Visualisation | Matplotlib, Seaborn, Plotly |
| App | Streamlit |
| Notebooks | Jupyter Notebook | VS Code|

All Python packages are listed in `requirements.txt`.

---

## 3. Notebooks

| Notebook | What it does |
|---|---|
| `01_data_cleaning.ipynb` | Loads the CSVs, checks shapes, dtypes, nulls and duplicates, cleans each table, removes orphaned rows, creates the MySQL tables and loads the data, then runs a test JOIN. |
| `02_sql_analysis.ipynb` | Connects to MySQL and answers 10 SQL questions. |
| `03_pandas_analysis.ipynb` | Answers 10 Pandas questions (totals, zero-value handling, profit and ROI, runtime outliers, duplicate titles, and others). |
| `04_visualizations.ipynb` | Four univariate, four bivariate and four multivariate charts. |

---


## 4. The Streamlit app

The app has three parts. The filters live in the sidebar, so they are visible on every page and shared by the other two pages. Their values are stored in `st.session_state`.

### Filters (sidebar)

- Genre multiselect (empty means all genres)
- Release-year range slider
- Minimum-rating slider
- Language selectbox
- A live count of how many movies match the current selection

### Page 1: Dashboard

All of it follows the current filters.

- KPI cards: total movies, genres represented, total actors, average rating
- Top 10 movies by revenue (bar chart)
- Movies per genre (bar chart)
- Budget vs revenue (scatter plot, log scale). Movies with an unknown (0) budget or revenue are left out.
- A text insight naming the highest-grossing genre and the top movie in the selection

### Page 2: Query Explorer

- A dropdown of five saved SQL queries: top 10 movies by revenue, top 10 actors, top 10 keywords, average rating by genre, and top 10 movies by number of keywords
- Each query only looks at the movies that match the filters
- The result is shown as a table (`st.dataframe`) and a bar chart, with a text insight below

---


## 5. Key insights and recommendations

1. Before 1980 there are very few films each year. There is a sharp increase throughout the 1990s and 2000s. In 2016 there were ~120 films.

2. Budget and Revenue are highly correlated (0.68). Revenue and Votes are also highly correlated (0.61). This means high budget films have higher revenues

3. Popularity is extremely skewed, and vote counts are skewed too: 
   `popularity` has a skew of 14.1 (mean 13.7 against a median of 10.4, maximum 438). `vote_count` has a skew of 2.4, and every movie has at least 475 votes.

4. Nearly all genres have seen a sharp increase in average revenue since the 1990s. Action went from $105M in the 1950s to $339M in the 2020s. The highest recent averages are Music ($649M, 2020s), Family ($635M in the 2010s) and ($607M, 2020s), Adventure ($551M in the 2010s). Animation also had a high average of $504M, 2020s), while Drama stays at about $100-175M.

5. The dataset brings together 2,452 movies across 19 genres, featuring 11,291 cast members and 2,846 crew members
---
