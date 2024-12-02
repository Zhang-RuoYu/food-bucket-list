from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///food_wheel.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'
db = SQLAlchemy(app)


# 資料庫模型
class FoodItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product = db.Column(db.String(100), nullable=False)
    size = db.Column(db.String(50), nullable=False)
    flavor = db.Column(db.String(100), nullable=False)

    def to_dict(self):
        return {"id": self.id, "product": self.product, "size": self.size, "flavor": self.flavor}


# 初始化資料庫
@app.before_request
def create_tables():
    if not hasattr(app, 'tables_created'):
        db.create_all()
        app.tables_created = True



# RESTful API
@app.route('/api/food', methods=['POST'])
def create_food():
    data = request.json
    food = FoodItem(product=data['product'], size=data['size'], flavor=data['flavor'])
    db.session.add(food)
    db.session.commit()
    return jsonify(food.to_dict()), 201


@app.route('/api/food', methods=['GET'])
def get_all_food():
    foods = FoodItem.query.all()
    return jsonify([food.to_dict() for food in foods])


@app.route('/api/food/<int:food_id>', methods=['PUT'])
def update_food(food_id):
    food = FoodItem.query.get_or_404(food_id)
    data = request.json
    food.product = data.get('product', food.product)
    food.size = data.get('size', food.size)
    food.flavor = data.get('flavor', food.flavor)
    db.session.commit()
    return jsonify(food.to_dict())


@app.route('/api/food/<int:food_id>', methods=['DELETE'])
def delete_food(food_id):
    food = FoodItem.query.get_or_404(food_id)
    db.session.delete(food)
    db.session.commit()
    return jsonify({'message': 'Food item deleted'})


# 前端頁面
@app.route('/')
def index():
    food_items = FoodItem.query.all()
    return render_template('index.html', food_items=food_items)


@app.route('/add', methods=['GET', 'POST'])
def add_food():
    if request.method == 'POST':
        product = request.form['product']
        size = request.form['size']
        flavor = request.form['flavor']
        food = FoodItem(product=product, size=size, flavor=flavor)
        db.session.add(food)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('add.html')


@app.route('/edit/<int:food_id>', methods=['GET', 'POST'])
def edit_food(food_id):
    food = FoodItem.query.get_or_404(food_id)
    if request.method == 'POST':
        food.product = request.form['product']
        food.size = request.form['size']
        food.flavor = request.form['flavor']
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('edit.html', food=food)


@app.route('/delete/<int:food_id>', methods=['POST'])
def delete_food_ui(food_id):
    food = FoodItem.query.get_or_404(food_id)
    db.session.delete(food)
    db.session.commit()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
