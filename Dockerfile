FROM python:3.10.9-buster
WORKDIR /app
RUN pip install --upgrade pip setuptools wheel
RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
RUN sh ./scripts/setup_container.sh

EXPOSE 5050

ENTRYPOINT ["sh", "./scripts/run_container.sh"]