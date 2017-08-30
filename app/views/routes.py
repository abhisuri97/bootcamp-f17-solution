from flask import render_template, jsonify
from app import app, db
from app.models.coordinates import Coordinate

import requests
import json

DIRECTIONS = {
    'left': 0,
    'up': 1,
    'right': 2,
    'down': 3
}


@app.route("/", methods=["GET", "POST"])
def index():
    coors = Coordinate.query.order_by(Coordinate.id.desc())
    return render_template('index.html', coors=coors)


@app.route("/walk/<x>/<y>/<dir>", methods=["POST"])
def walk(x, y, dir):
    query = requests.get(app.config['QUERY_URL'] +
                         '/{}/{}/{}'.format(x, y, DIRECTIONS[dir]))
    result = json.loads(query.content)
    print(result)
    new_coordinate = Coordinate(x, y, dir, result['validMove'])
    db.session.add(new_coordinate)
    db.session.commit()
    return jsonify(result)
