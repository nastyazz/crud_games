from flask import Flask, jsonify, request
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.sql import SQL, Literal
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.json.ensure_ascii = False

connection = psycopg2.connect(
    host=os.getenv('POSTGRES_HOST') if os.getenv('DEBUG_MODE') == 'false' else 'localhost',
    port=os.getenv('POSTGRES_PORT'),
    database=os.getenv('POSTGRES_DB'),
    user=os.getenv('POSTGRES_USER'),
    password=os.getenv('POSTGRES_PASSWORD'),
    cursor_factory=RealDictCursor
)
connection.autocommit = True

@app.get("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.get("/games")
def get_games():
    query = """
with
  games_with_buyer as (
    select g.id, g.title, g.genre, g.price,
       coalesce(jsonb_agg(jsonb_build_object(
           'id', b.id, 'nickname', b.nickname, 'date_registrate', b.date_registrate))
           filter (where b.id is not null), '[]') as buyers
    from games_data.games g
    left join games_data.games_to_buyer gb on g.id = gb.games_id
    left join games_data.buyer b on gb.buyer_id = b.id
    group by g.id
  ),
  games_with_comment as (
    select gwb.id, gwb.title, gwb.genre, gwb.price, gwb.buyers,
           coalesce(jsonb_agg(jsonb_build_object(
               'id', c.id, 'description', c.description_, 'date_public', c.date_public, 'estimation', c.estimation))
               filter (where c.id is not null), '[]') as comments
    from games_with_buyer gwb
    left join games_data.comment c on gwb.id = c.game_id
    group by gwb.id, gwb.title, gwb.genre, gwb.price, gwb.buyers
  )
select g.id, g.title, g.genre, g.price, g.buyers, g.comments
from games_with_comment g;
"""


    with connection.cursor() as cursor:
        cursor.execute(query)
        result = cursor.fetchall()

    return jsonify(result)


@app.post('/games/create')
def create_game():
    body = request.json

    if not body or 'title' not in body or 'genre' not in body or 'price' not in body:
        return jsonify({"error": "Некорректное тело запроса"}), 400

    title = body['title']
    genre = body['genre']
    price = body['price']

    query = SQL("""
    insert into games_data.games(title, genre, price)
    values ({title}, {genre}, {price})
    returning id
    """).format(title=Literal(title), genre=Literal(genre), price=Literal(price))

    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
            result = cursor.fetchone()
        return jsonify(result), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.put('/games/update')
def update_game():
    body = request.json

    if not body or 'id' not in body or 'title' not in body or 'genre' not in body or 'price' not in body:
        return jsonify({"error": "Некорректное тело запроса"}), 400

    id = body['id']
    title = body['title']
    genre = body['genre']
    price = body['price']

    query = SQL("""
    update games_data.games
    set 
        title = {title}, 
        genre = {genre},
        price = {price}
    where id = {id}
    returning id
    """).format(title=Literal(title), genre=Literal(genre),
                price=Literal(price), id=Literal(id))

    with connection.cursor() as cursor:
        cursor.execute(query)
        result = cursor.fetchall()

    if len(result) == 0:
        return '', 404

    return '', 204

@app.delete('/games/delete')
def delete_game():
    body = request.json

    if not body or 'id' not in body:
        return jsonify({"error": "Некорректное тело запроса"}), 400

    id = body['id']

    delete_game_links = SQL(
        "delete from games_data.games_to_buyer where games_id = {id}").format(
            id=Literal(id))
    delete_game = SQL("delete from games_data.games where id = {id} returning id").format(
        id=Literal(id))

    with connection.cursor() as cursor:
        cursor.execute(delete_game_links)
        cursor.execute(delete_game)
        result = cursor.fetchall()

    if len(result) == 0:
        return '', 404

    return '', 204

if __name__ == '__main__':
    app.run(port=os.getenv('FLASK_PORT'))
