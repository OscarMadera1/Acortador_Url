import unittest
from app import app


class URLShortenerTests(unittest.TestCase):
    def setUp(self):
        app.testing = True
        self.app = app.test_client()

    def test_register(self):
        response = self.app.post(
            "/register", data={"username": "testuser", "password": "testpassword"}
        )
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertIn("message", data)
        self.assertEqual(data["message"], "Registro exitoso")

    def test_login(self):
        response = self.app.post(
            "/login", data={"username": "testuser", "password": "testpassword"}
        )
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertIn("message", data)
        self.assertEqual(data["message"], "Inicio de sesión exitoso")

    def test_shorten(self):
        response = self.app.post(
            "/shorten", data={"original_url": "https://www.example.com"}
        )
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertIn("short_url", data)

    def test_redirect_to_original_url(self):
        response = self.app.get("/abcd1234")
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertIn("error", data)
        self.assertEqual(data["error"], "URL no encontrada")
