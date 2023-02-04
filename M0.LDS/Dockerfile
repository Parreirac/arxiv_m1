FROM python:3.9-alpine

ADD . /app

WORKDIR /app


#useful when pushing to Docker Hub
#MAINTANER Your Name "youremail@domain.tld" devient maintenant :
LABEL org.opencontainers.image.authors="me@home.org"


# By copying over requirements first, we make sure that Docker will cache
# our installed requirements rather than reinstall them on every build
COPY requirements.txt /app/requirements.txt

RUN pip --no-cache-dir install -r requirements.txt   # TODO tester la différence
#RUN pip install -r requirements.txt


# Now copy in our code, and run it
COPY ./app /app

EXPOSE 5000

ENTRYPOINT ["python"]

# execute the script:
CMD [ "main.py"]




