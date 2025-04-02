FROM python:3.10-slim-bullseye

COPY . /csat

WORKDIR /csat

# RUN curl https://dev.mysql.com/downloads/file/?id=519241 --output mysql-apt-config_0.8.25-1_all.deb \
#     && dpkg -i mysql-apt-config_0.8.25-1_all.deb 
# # && dpkg -i mysql-apt-config_0.8.25-1_all.deb


RUN apt-get update --fix-missing \
    && apt-get -y install --no-install-recommends postgresql-client git default-mysql-client\
    && pip install --upgrade pip

# ADD requirements.txt .
RUN pip install -r requirements.txt
