from flask import (
    Flask,
    render_template
)

from database.models import Property

app = Flask(__name__)


@app.route("/")
def home():

    properties = Property.query.limit(
        10
    ).all()

    return render_template(
        "index.html",
        properties=properties
    )


@app.route("/property/<int:id>")
def property_detail(id):

    property = Property.query.get_or_404(
        id
    )

    return render_template(
        "property.html",
        property=property
    )