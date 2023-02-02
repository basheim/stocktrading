FROM python:3.10.9-buster
WORKDIR /app
RUN pip install --upgrade pip setuptools wheel
RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
RUN sh ./scripts/add_aws.sh

RUN addgroup usergroup
RUN adduser --no-create-home --disabled-password --ingroup usergroup appuser
RUN chown -R appuser:usergroup /app
USER appuser

EXPOSE 5050

ENTRYPOINT ["gunicorn", "-w", "1", "-b", "0.0.0.0:5050", "--log-level", "info", "--access-logfile", "-", "--error-logfile", "-","app:app"]