from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://your_username:your_password@localhost/perfume_matching'
db = SQLAlchemy(app)

class Perfume(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    brand = db.Column(db.String(255), nullable=False)
    notes = db.Column(db.Text)
    price = db.Column(db.DECIMAL(10, 2))
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())
    updated_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), server_onupdate=db.func.current_timestamp())

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search_perfumes():
    user_input = request.form.get('perfume_name')
    
    # Sample matching logic (you should refine this)
    matches = Perfume.query.filter(Perfume.name.ilike(f'%{user_input}%')).all()
    
    return render_template('results.html', matches=matches)

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
