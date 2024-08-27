FROM python:3.12-slim

WORKDIR /app

COPY ./app /app/
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

ENV ASB_CONNECTION_STRING=pass
ENV ASB_QUEUE=pass
ENV ADO_ORG=pass
ENV ADO_PROJECT=pass
ENV ADO_PAT=pass
ENV ASB_POLL_INTERVAL_SECONDS=pass

CMD ["python", "-u", "main.py"]