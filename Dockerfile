#using python 
FROM python:3.11-slim

#set directory in container
WORKDIR /app

#get requirements and pip install them 
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

#copy everything else into container
COPY . . 

#Expose default port for flask
EXPOSE 5000

#set env variables tellling flask how to run
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

#booting up the server
CMD ["python", "app.py"]

# used samples found in https://docs.docker.com/reference/samples/flask/
