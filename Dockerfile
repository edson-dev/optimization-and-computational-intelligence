#docker build -t dag .
#docker push dag
#docker run dag
FROM python:3.12
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY src .
CMD ["python", "./main.py"]