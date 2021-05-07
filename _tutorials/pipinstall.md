# installs

## pre apt installs

```
sudo apt update
sudo apt upgrade
```

## apt installs

```
sudo apt update
sudo apt upgrade
sudo apt install python3
sudo apt install pip
```

maybe not needed:
```
sudo apt install libmysqlclient-dev
```

## pip installs

```
pip install virtualenv
pip install django
pip install django-crispy-forms
pip install django-multiselectfield
pip install django_timedeltatemplatefilter

// pip install -U wheel (required for mysqlclient)
// sudo apt-get install libpython3.9-dev (important)
// pip install mysqlclient

// pip install mysql-connector-python

pip install mysql-connector
pip install Pillow
pip install django_group_by
pip install celery
pip install django-celery

pip install authlib
pip install jsonify
pip install oauthlib
pip install djangorestframework
```

## install docker / database requirements

```
sudo apt-get remove docker docker-engine docker.io containerd runc
```

```
 sudo apt-get install \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release
```

```
 curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
```

```
echo \
  "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
 ```

```
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io
```

```
sudo docker --version
```

```
sudo apt install docker-compose
sudo apt install software-properties-common
```

### TODO
docker compose file...