sudo systemctl start mariadb.service
python -m uvicorn app.main:app --reload
Requirements:

- For pymupdf tesseract needs to be installed for the language deu on the system.
- All the tables in daatabase_init.sql must be in a database called Unizeug with password: DBPassword
- requirements.txt or just all the python modules until pytohn stops complaining. I recommend to use a venv for this project.
  Just information I dont want to forget:
- TISS API maby not nessecarry: https://tiss.tuwien.ac.at/api/course/101685-2024W
