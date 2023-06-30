FROM python:3.11
ENV PYTHONUNBUFFERED 1

RUN apt-get update -y
RUN apt-get install binutils libproj-dev gdal-bin -y

WORKDIR /app
RUN pip install pipenv
COPY ./ ./
RUN pipenv install --system --deploy --ignore-pipfile

EXPOSE 80

CMD ["bash", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:80"]

