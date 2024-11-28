FROM python:3.9-slim
COPY . /app
WORKDIR /app
RUN apt-get update && apt-get install -y gcc && pip3 install --upgrade pip && pip3 install -r requirements.txt
EXPOSE 5001
CMD ["gunicorn", "secretgarden.run:app", "-c", "gunicorn.conf.py"]
