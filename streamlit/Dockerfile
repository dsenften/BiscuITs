FROM python:3.9-slim

WORKDIR /app

RUN pip install streamlit requests

COPY streamlit_app.py .

EXPOSE 8501

CMD ["streamlit", "run", "streamlit_app.py", "--server.enableCORS", "false", "--server.port", "8501"]
