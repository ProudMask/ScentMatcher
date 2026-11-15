import unittest
from app import create_app, db, Perfume, parse_notes, recommend


class MatchingTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'})
        self.context = self.app.app_context()
        self.context.push()
        db.create_all()
        db.session.add_all([Perfume(name='Rose', brand='Demo', notes='rose, musk, vanilla'), Perfume(name='Garden', brand='Demo', notes='rose, jasmine, musk'), Perfume(name='Citrus', brand='Demo', notes=None)])
        db.session.commit()
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.context.pop()

    def test_score_excludes_self_and_missing_notes(self):
        perfumes = db.session.execute(db.select(Perfume).order_by(Perfume.id)).scalars().all()
        results = recommend(perfumes[0], perfumes)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['perfume'].name, 'Garden')
        self.assertEqual(results[0]['score'], 0.5)

    def test_normalization_preserves_phrases(self):
        self.assertEqual(parse_notes(' White Musk;rose, ROSE '), {'white musk', 'rose'})

    def test_empty_and_missing_input(self):
        for data in ({}, {'perfume_name': '  '}):
            self.assertEqual(self.client.post('/search', data=data).status_code, 400)

    def test_exact_search_and_partial_choice(self):
        response = self.client.post('/search', data={'perfume_name': ' rose '})
        self.assertIn(b'Garden', response.data)
        self.assertIn(b'50.0%', response.data)
        self.assertIn(b'exact perfume name', self.client.post('/search', data={'perfume_name': 'Gar'}).data)

    def test_literal_wildcards_and_unknown(self):
        for query in ('%', '_', 'unknown'):
            self.assertIn(b'No perfume found', self.client.post('/search', data={'perfume_name': query}).data)

    def test_seed_is_repeatable(self):
        runner = self.app.test_cli_runner()
        for _ in range(2):
            self.assertEqual(runner.invoke(args=['seed-demo']).exit_code, 0)
        self.assertEqual(db.session.query(Perfume).filter_by(brand='Synthetic Demo').count(), 4)


if __name__ == '__main__':
    unittest.main()
