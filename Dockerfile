FROM python:3.6
COPY ./topics.json /tmp
WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "./app.py"]