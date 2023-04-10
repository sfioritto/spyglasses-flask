import unittest
import json
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
        response = self.client.get('/posts')
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

    def test_create_post(self):
        # Test creating a post with valid data
        data = {
            'content': 'This is a test post.',
            'post_type': 'public'
        }
        response = self.client.post(
            '/posts', data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        response_data = json.loads(response.data)
        self.assertIn('post_id', response_data)
        self.assertIn('message', response_data)
        self.assertEqual(response_data['message'], 'Post created successfully')

        # Test creating a post with missing data
        data = {
            'content': 'This is another test post.'
        }
        response = self.client.post(
            '/posts', data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.data)
        self.assertIn('error', response_data)
        self.assertEqual(
            response_data['error'], 'Missing content or post_type in request data')

    def test_get_post(self):
        post = Post(content='Test content', post_type='public')
        db.session.add(post)
        db.session.commit()

        response = self.client.get(f'/posts/{post.id}')
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertIn('post', response_data)
        self.assertEqual(response_data['post']['content'], 'Test content')
        self.assertEqual(response_data['post']['post_type'], 'public')

        response = self.client.get('/posts/9999')
        self.assertEqual(response.status_code, 404)


if __name__ == '__main__':
    unittest.main()
