from flask import render_template, jsonify
from app import app, db
from app.models.coordinates import Coordinate

import requests
import json

@app.route("/")
def index():
    coors = Coordinate.query.order_by(Coordinate.id.desc()).all()
    return render_template('index.html', coors=coors)


@app.route("/walk/<x>/<y>/<dir>")
def walk(x, y, dir):
    query = requests.get(app.config['QUERY_URL'] +
                         '/{}/{}/{}'.format(x, y, dir))
    result = json.loads(query.content)
    new_coordinate = Coordinate(x, y, dir, result['validMove'])
    db.session.add(new_coordinate)
    db.session.commit()
    return jsonify(result)
