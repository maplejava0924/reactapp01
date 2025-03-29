# LangGraph-Supervisorの要件 Python Version >= 3.10
FROM python:3.10.2-buster

ENV LANG C.UTF-8
ENV TZ Asia/Tokyo

# pipとセットアップツールのアップグレード：LangGraph-Supervisorのため
RUN pip install --upgrade pip setuptools wheel

COPY ./docker/backend/requirements.txt requirements.txt
RUN pip install -r requirements.txt

#コンテナ起動時の初期カレントディレクトリ
WORKDIR /app

ENTRYPOINT ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000", "--reload"]