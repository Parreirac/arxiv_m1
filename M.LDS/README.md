Ce module est la déclinaison du projet fil rouge pour le cours languages en data-sciences

Goal: Write a Flask application that provides an API that reads an uploaded pdf,
      extract its metadata & text them available for consumption by the user.

Use a Python package to handle PDF processing (probably PDFMiner)
Use a git repository for sources
Use a requirements.txt file to specify dependencies and their versions

Possible API:
POST	/documents				upload a new pdf, responds a document ID
GET		/documents/<id> 		describe document processing state (pending, success, failure), metadata and links to contents
GET		/text/<id>.txt 		a way to read the extracted text
Possibly use a (redis celery) queue to analyze the document asynchronously
Check warnings with Pylint/flake8, reformat the code with black & isort
Check code coverage with pytest-cov

