# covid19api
Building an API that returns the current information about the Coronavirus (Covid-19), the scrapper collects the data per country clean it and stores it to mongoDB.

# Scrapper
Collects data from [World Meters](https://www.worldometers.info/coronavirus/) every hour and stores it in a MongoDB.

Some assumptions:

    > MongoDB is install in system as local host.
    > Pipenv is install.

The scrapper runs independently from the API. You can install the virtual enviroment using Pipenv at the top level folder.

Run code as:
```
- pipenv shell
- pipenv install
- python scrapper.py
```

# API
TBD
