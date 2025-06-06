#docker build -t edsonxp/dagbpsk .
#docker push edsonxp/dagbpsk
#docker run edsonxp/dagbpsk
FROM python:3.12
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src/ .
CMD ["python", "main.py"]