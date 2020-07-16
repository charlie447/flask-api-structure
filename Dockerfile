FROM python:3.6-alpine

RUN adduser -D charlie

WORKDIR /home/charlie

COPY requirements.txt requirements.txt
RUN python -m venv venv
RUN venv/bin/pip install -r requirements.txt
RUN venv/bin/pip install gunicorn

COPY app app
COPY migrations migrations
COPY start.py config.py boot.sh ./
RUN chmod +x boot.sh

ENV FLASK_APP start.py

RUN chown -R charlie:charlie ./
USER charlie

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]