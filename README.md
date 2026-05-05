Backend:

cd solarvida/backend

pip install flask flask-jwt-extended flask-cors bcrypt --break-system-packages 2>&1 | tail -5

python3 app.py / flask run --host=0.0.0.0 --port=5000

Frontend:

cd solarvida/frontend

python3 -m http.server 5500

Acesso:

Backend → http://127.0.0.1:5000

Frontend → http://127.0.0.1:5500

