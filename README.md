# Local development

## Requirements
- pipenv
- docker
- heroku-cli

## Commands for local development & deployment

We have a Makefile with common commands.

Do `make pip` once to install dependencies (using pipenv). Repeat every time the dependencies change.
Create a copy of `env.example` like so:
`cp env.example .env`
and populate `.env` with the correct values for OPENHUMANS and GITHUB credentials.

Every time you want to run locally, do `make deps` and then `make local`. The app will be available at `127.0.0.1:5000`

To deploy the current version to heroku, do `make deploy`.


# The OH Github integration

<!-- [![Build Status](https://travis-ci.org/OpenHumans/oh-moves-source.svg?branch=master)](https://travis-ci.org/OpenHumans/oh-moves-source) -->

This repository provides a `Django` application that interfaces both with the `Open Humans` API and the `Github` API to collect commit data from `Github` and uploading it into `Open Humans`. It is based on the https://github.com/OpenHumans/oh-data-demo-template repository.

For a user the workflow is the following:

1. User goes to the website provided by this repo
2. A user signs up/signs in with Open Humans and authorizes the `Github` integration on `Open Humans`
3. This redirects the user back to this Github-integration website
4. The user is redirected starts the authorization with `Github`. For this they are redirected to the Github page
5. After a user has authorized both `Open Humans` & `Github` their `Github` data will be requested and ultimately saved as a file in Open Humans.
6. Regular updates of the data are triggered daily to keep the data on Open Humans up to date.

Getting the data from `Github` and uploading it to Open Humans has a couple of challenges:
1. The `Github` API uses rate limits, which need to be respected and going over the rate limit would not yield more data but just errors
2. Getting all the data from `Github` takes a while, not only because of the rate limits, but also because it can be a lot of data
3. We want to regularly update data and take into account data we already did upload to Open Humans.

For this reason this application makes good use of background tasks with `Celery` and the Python module `requests_respectful`, which keeps track of API limits by storing limits in a `redis` database. As `redis` is already used for `Celery` as well this does not increase the number of non-python dependencies.

## setup for requests_respectful
The settings for `requests_respectful` can be found in `demotemplate/settings.py`.

```
rr = RespectfulRequester()
rr.register_realm("github", max_requests=5000, timespan=3600)
```
By registering a `realm` we set up a namespace for the github requests and specify that at max. 60 requests per 60 seconds can be made. If we would make an additional request this would yield a `RequestsRespectfulRateLimitedError`.

## setup for Celery
The settings for Celery can be found in `datauploader/celery.py`. These settings apply globally for our application. The Celery task itself can be found in `datauploader/tasks.py`. The main task for requesting & processing the github data is `process_github()` in that file.

## Doing automatic updates of the Github data
This can be done by regularly enqueuing `process_github` tasks with `Celery`. As `Heroku` does not offer another cheap way of doing it we can use a `management task` for this that will be called daily by the `heroku scheduler`.

This Management task lives in `main/management/commands/update_data.py`. Each time it is called it iterates over all `Github` user models and checks when the last update was performed. If the last update happened more than 4 days ago it will put a `process_github` task into the `Celery` queue.

## Folder structure

- `datauploader` contains both
  - the celery settings in `celery.py`
  - and the actual `celery tasks` in `tasks.py`
- `demotemplate`contains
  - the general app's `settings.py`
- `main` contains the
  - `views.py` for the actual views
  - the `templates/` for the views
  - the `urls.py` for routing
  - the `models.py` that describe the `Github User Model`
  - the `tests/` for the whole application
  - the `management/` commands
- `open_humans` contains
  - the `Open Humans user model`
