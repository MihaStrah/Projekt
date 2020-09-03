from app import server

#konfiguracija wsgi strežnika
if __name__ == "__main__":
    server.run(host='0.0.0.0', port=8000)