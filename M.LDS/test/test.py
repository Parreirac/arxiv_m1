"""
Test module for the app
"""
import ast
import unittest

from flask import current_app

from main import app


class AppTestCase(unittest.TestCase):
    """unittest for the app"""
    def setUp(self):
        self.ctx = app.app_context()
        self.ctx.push()
        self.client = app.test_client()

    def tearDown(self):
        self.ctx.pop()

    def test_app_exists(self):
        """does app exist ?"""
        self.assertFalse(current_app is None)

    def test_app_is_debug(self):
        """are-we in debug mode ?"""
        self.assertTrue(current_app.config['DEBUG'])

    def test_app_delete_session(self):
        """test /delete_session route"""
        response = self.client.get("/delete_session", data={"content": "hello world"})
        assert response.status_code == 200
        assert "<h1>Session deleted!</h1>" == response.get_data(as_text=True)

    def test_home_page(self):
        """test home page"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_upload_file1(self):
        """Very small file to test. No watermark"""
        filename = "testPdf.pdf"

        with open(filename, "rb") as your_file:
            response = self.client.post("/upload", data=dict(file=your_file, ) \
                                        ,content_type='multipart/form-data' )

        assert response.status_code == 200
        response = self.client.get('/getmetadata/' + filename)
        metadata = ast.literal_eval(response.get_data(as_text=True))
        assert 5 == len(metadata)
        assert metadata.get("/Author") == "tof"
        assert metadata.get("/CreationDate") == "D:20230130090911+01'00'"
        assert metadata.get("/ModDate") == "D:20230130090911+01'00'"
        assert metadata.get("/Producer") == "Microsoft: Print To PDF"
        assert metadata.get("/Title") == "Microsoft Word - Document1"

        response = self.client.get('/gettext/' + filename)
        text = ast.literal_eval(response.get_data(as_text=True))
        assert text.get("/Text") == "Fichier pdf de test. "

        response = self.client.get('/getarxiveid/' + filename)
        arxive_id = ast.literal_eval(response.get_data(as_text=True))
        assert arxive_id.get("cat") == ""
        assert arxive_id.get("date") == ""
        assert arxive_id.get("id") == ""

    def test_upload_file2(self):
        """article from arxive in order to test watermark"""
        filename = "0709.4655.pdf"

        with open(filename, "rb") as file:
            response = self.client.post("/upload", data=dict(file=file, ), \
                                        content_type='multipart/form-data' )

        assert response.status_code == 200
        response = self.client.get('/getarxiveid/' + filename)
        arxive_id = ast.literal_eval(response.get_data(as_text=True))
        assert arxive_id.get("cat") == "[cs.DB]"
        assert arxive_id.get("date") == "28 Sep 2007"
        assert arxive_id.get("id") == "arXiv:0709.4655v1"


if __name__ == "__main__":
    unittest.main()
