"""A transparent note-overlap baseline for perfume recommendations."""
import os
import re
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Perfume(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    brand = db.Column(db.String(255), nullable=False)
    notes = db.Column(db.Text)
    price = db.Column(db.Numeric(10, 2))
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, server_default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())


def parse_notes(value):
    """Treat comma/semicolon-separated phrases as notes, preserving multiword notes."""
    return {part.strip().casefold() for part in re.split(r'[,;]', value or '') if part.strip()}


def recommend(source, catalog, limit=5):
    source_notes = parse_notes(source.notes)
    results = []
    for candidate in catalog:
        if candidate.id == source.id:
            continue
        notes = parse_notes(candidate.notes)
        shared = source_notes & notes
        if shared:
            results.append({'perfume': candidate, 'score': len(shared) / len(source_notes | notes), 'shared_notes': sorted(shared)})
    return sorted(results, key=lambda item: (-item['score'], item['perfume'].name.casefold(), item['perfume'].id))[:limit]


def create_app(config=None):
    app = Flask(__name__)
    app.config.update(SQLALCHEMY_DATABASE_URI=os.getenv('DATABASE_URL', 'sqlite:///perfumes.db'), SQLALCHEMY_TRACK_MODIFICATIONS=False)
    if config:
        app.config.update(config)
    db.init_app(app)

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/search', methods=['POST'])
    def search_perfumes():
        query = (request.form.get('perfume_name') or '').strip()
        if not query or len(query) > 255:
            return render_template('index.html', error='Enter a perfume name between 1 and 255 characters.'), 400
        catalog = db.session.execute(db.select(Perfume).order_by(Perfume.name, Perfume.id)).scalars().all()
        sources = [p for p in catalog if p.name.casefold() == query.casefold()]
        choices = []
        source = None
        matches = []
        message = None
        if len(sources) == 1:
            source = sources[0]
            matches = recommend(source, catalog)
            if not matches:
                message = 'No alternatives with shared notes were found.'
        elif len(sources) > 1:
            message = 'Several perfumes have this name. Use a catalog with unique perfume names for this baseline.'
        else:
            choices = [p for p in catalog if query.casefold() in p.name.casefold()][:10]
            message = 'Enter an exact perfume name to find alternatives.' if choices else 'No perfume found. Check the spelling or initialize the demo catalog.'
        return render_template('results.html', source=source, matches=matches, choices=choices, message=message)

    @app.cli.command('init-db')
    def init_db():
        db.create_all()
        print('Database tables created.')

    @app.cli.command('seed-demo')
    def seed_demo():
        db.create_all()
        rows = [('Demo Rose', 'rose, musk, vanilla'), ('Demo Garden', 'rose, jasmine, musk'), ('Demo Amber', 'amber, vanilla, musk'), ('Demo Citrus', 'lemon, bergamot, cedar')]
        for name, notes in rows:
            if db.session.execute(db.select(Perfume).filter_by(name=name, brand='Synthetic Demo')).scalar_one_or_none() is None:
                db.session.add(Perfume(name=name, brand='Synthetic Demo', notes=notes))
        db.session.commit()
        print('Synthetic demonstration catalog ready.')

    return app


app = create_app()

if __name__ == '__main__':
    app.run()
