FROM python:3

WORKDIR /user/src/app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN pip install ./en_core_web_sm-3.7.1

CMD [ "python", "app.py" ]