FROM python:3.12

WORKDIR /app
COPY . .
RUN pip install -r requirements.txt

ENV PORT=80
ENV API_KEY=123456
ENV GOOGLE_API_KEY=YOUR_GOOGLE_API_KEY
ENV OPENAI_API_KEY=OPENAI_API_KEY

EXPOSE $PORT

CMD ["sh", "-c", "uvicorn app:app --no-server-header --workers 1 --host 0.0.0.0 --port $PORT"]