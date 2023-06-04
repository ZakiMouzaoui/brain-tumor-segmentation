FROM python:3.10.6

WORKDIR /app

COPY requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

ENTRYPOINT [ "streamlit", "run"]

CMD ["main.py"]