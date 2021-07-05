source env/bin/activate
uvicorn app:app --port 8003 --host 0.0.0.0 --timeout-keep-alive 30 --reload
