FROM python

WORKDIR /app

COPY requirement.txt requirement.txt

RUN pip install -r requirement.txt

COPY . .

CMD [ "python", "manage.py", "runserver", "0.0.0.0:8000" ]