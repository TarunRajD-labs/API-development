from flask import Flask, request, jsonify, render_template, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os, csv

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///items.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

print("✅ Database path:", os.path.abspath("items.db"))

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at.isoformat()
        }

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/market')
def market():
    return render_template('market.html')

@app.route('/items', methods=['GET'])
def get_items():
    items = Item.query.order_by(Item.created_at.desc()).all()
    return jsonify([item.to_dict() for item in items])

@app.route('/items', methods=['POST'])
def create_item():
    data = request.get_json()
    new_item = Item(name=data['name'], description=data.get('description'))
    db.session.add(new_item)
    db.session.commit()
    print(f"✅ Added to DB: {new_item.name} - {new_item.description}")
    return jsonify(new_item.to_dict()), 201

@app.route('/items/<int:item_id>', methods=['PUT'])
def update_item(item_id):
    item = Item.query.get_or_404(item_id)
    data = request.get_json()
    item.name = data.get('name', item.name)
    item.description = data.get('description', item.description)
    db.session.commit()
    print(f"✏️ Updated ID {item.id}")
    return jsonify(item.to_dict())

@app.route('/items/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    item = Item.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    print(f"🗑️ Deleted ID {item.id}")
    return jsonify({"message": "Item deleted"})

@app.route('/export')
def export():
    items = Item.query.all()
    with open("items.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["ID", "Name", "Description", "Created At"])
        for item in items:
            writer.writerow([item.id, item.name, item.description, item.created_at])
    return send_file("items.csv", as_attachment=True)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
