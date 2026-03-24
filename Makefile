.PHONY: start
start:
	uvicorn app.main:app --reload --host 0.0.0.0

