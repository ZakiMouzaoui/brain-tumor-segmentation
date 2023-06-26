FROM python:3.10.6

WORKDIR /app

COPY requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

RUN apt-get update && apt-get install -y python3-opencv
RUN pip install opencv-python

COPY . .

EXPOSE 8501

ENTRYPOINT [ "streamlit", "run"]

CMD ["main.py"]