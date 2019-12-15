FROM python:3.7-stretch

WORKDIR /opt
ENV PYTHONPATH=/opt

COPY requirements.txt requirements.txt

RUN pip3 install --no-cache-dir -r requirements.txt

EXPOSE 8080

COPY . .

ENTRYPOINT ["python3", "main.py"]
