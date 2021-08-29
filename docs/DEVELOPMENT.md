### Requirements

Python 3.7 or greater as well as Python pip3

### Setting up environment

Setup python virtual environment
```
pip3 install virtualenv
```

Now create a virtual environment
```
virtualenv venv
```

Active your virtual environment:
```
source venv/bin/activate
```

Install requirements within venv
```
pipenv install -r requirements.txt
```
This will create Pipfile and Pipfile.lock