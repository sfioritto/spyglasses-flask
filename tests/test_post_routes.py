import unittest
from flask import Flask
from flask_testing import TestCase
from spyglasses import create_app
from spyglasses.models import db, Post


class TestPostRoutes(TestCase):
    def create_app(self):
        return create_app()

    def setUp(self):
        db.create_all()

        # Create sample data
        post1 = Post(content="Test post 1 content",
                     blurb="Test post 1 blurb", post_type="text")
        post2 = Post(content="Test post 2 content",
                     blurb="Test post 2 blurb", post_type="text")
        db.session.add_all([post1, post2])
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_get_posts(self):
        response = self.client.get('/api/v1/posts')
        print(response.data)
        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertEqual(len(data), 2)
        for post in data:
            self.assertNotIn('content', post)
            self.assertIn('id', post)
            self.assertIn('blurb', post)
            self.assertIn('post_type', post)
            self.assertIn('created_at', post)
            self.assertIn('updated_at', post)


if __name__ == '__main__':
    unittest.main()
