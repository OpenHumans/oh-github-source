# Setup

This is intended to be a detailed local setup document with explanations for this repository.

## Table of Contents

- [Cloning this template](#cloning-this-template)
- [Setting up local environment](#setting-up-local-environment)
    + [Installing Heroku CLI](#installing-heroku-cli)
    + [Installing Redis](#installing-redis)
    + [Python](#python)
    + [pip](#pip)
    + [Virtual environments](#virtual-environments)
    + [Installing dependencies](#installing-dependencies)
- [Creating an Open Humans project](#creating-an-open-humans-project)
- [Final steps of app setup](#final-steps-of-app-setup)
- [Heroku deployment](#heroku-deployment)
    + [Heroku setup](#heroku-setup)
    + [Creating a Heroku application](#creating-a-heroku-application)
    + [App configuration](#app-configuration)
- [Adding dummy data](#adding-dummy-data)
- [Next steps](#next-steps)
    + [Under the hood](#under-the-hood)
    + [Editing the template](#editing-the-template)
- [Getting help](#getting-help)

## Cloning this template

In your terminal, navigate to the folder in which you want to store this repo, and enter the command

`$ git clone git@github.com:OpenHumans/oh-data-demo-template.git`

This should create a new folder named `oh-data-demo-template` which contains all the code to create the working demo.

## Setting up local environment

### Installing Heroku CLI

The [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli#download-and-install) is a local command line tool that helps us run and eventually deploy our application to Heroku. To install:

**macOS:**

if you have [Homebrew](https://brew.sh/) installed (recommended):

`$ brew install heroku/brew/heroku`

otherwise follow [these instructions](https://devcenter.heroku.com/articles/heroku-cli#download-and-install)

**Linux:**

`$ wget -qO- https://cli-assets.heroku.com/install-ubuntu.sh | sh`

**Windows:**

[Click the link](https://devcenter.heroku.com/articles/heroku-cli#download-and-install) and choose an installer to download

### Installing Redis

[Redis](https://redis.io/) is an open source, in-memory data structure store, used as a database, cache and [message broker](https://en.wikipedia.org/wiki/Message_broker) used by this application for Celery and Requests Respectful.

To install Redis you have a few options (just do 1 of them):
1. Follow [these instructions](https://redis.io/topics/quickstart)
2. (macOS only) `brew install redis` and then `redis-server /usr/local/etc/redis.conf`
3. Install with Docker and run container in background:

`$ docker create --name redis-db -p 6379:6379 redis:alpine`
`$ sudo service docker start`

To set it running with Docker on very popular Ubuntu and other Debian based systems, it will likely be started for you after you install the package, but can also start it manually with:

`$ docker start redis-db`.

### Python

This version of the template runs on [Python 3](https://www.python.org/downloads/). We recommend that you use this version, but you can still use the [old version](http://github.com/OpenHumans/oh-data-source-template) which requires only Python 2.

Please note that if you are working on a Mac, it is strongly advised that you install a fresh version of Python. The version that ships with OSX is not suitable for development and use with third party packages. Instructions for setting up your Python environment properly in OSX can be found [here](http://docs.python-guide.org/en/latest/starting/install/osx/).

### pip

[pip](https://pypi.python.org/pypi/pip) is a package management system used to install and manage software packages written in Python. It is available [here](https://pip.pypa.io/en/stable/installing/). Check your `pip` version by entering `$ pip --version` to make sure that it is working with Python 3; you may have to use the command `pip3`.

### Virtual environments

Virtual environments are useful when developing apps with lots of dependencies since they enable us to install software locally for a specific project, without it being present globally. Using a virtual environment allows us to use specific versions of each program and/or package for this project only, without affecting the versions that are used elsewhere on your machine.

We will set up the virtual environment here, and then work from within it for the remainder of this guide.

1. install the Python package  [pipenv](http://pipenv.readthedocs.io/en/latest/), using pip: `$ pip install pipenv` or `$ pip3 install pipenv`
2. navigate to your project folder for this template repo, and enter the command `$ pipenv --python 3.6`

This command should output some information about how it's creating a virtual environment for us with some path information about it.

Whenever we use pip or python commands, this virtual environment will be used for the remainder of this tutorial.

You can work from within this environment with `$ pipenv shell`

If you want to run commands from outside of this shell, you can type `$ pipenv run ___`, for example, `$ pipenv run python`.

### Installing dependencies

You can install all dependencies with:

`$ pipenv install`

*Note: This will install the dependencies for this project from the Pipfile and Pipfile.lock. If you have issues with installing all of the requirements at once, read the error(s) as there may be some other requirement missing locally (such as Postgres). If you still have problems, [raise an issue on Github](http://github.com/OpenHumans/oh-data-source-template/issues)*.

### Environment file

The environment file (`.env`) contains configurations for running the application. This file will be used to set up the environmental variables that `Django` uses to set up everything (The deployment to `heroku` does not use this file, instead you can use their website to set up these variables. See more below under `heroku`). The `.env` file **should never be committed to git** and should be kept private as it contains secrets.  First copy the contents of the template environment file, `env.example`, paste into a new file, and save with the filename `.env`(use `$ cp env.example .env`) we will go back and alter the contents after creating a project on the Open Humans site. The `.env` filename should already be in your `.gitignore`, but it is worth double-checking to make sure.

## Creating an Open Humans project

Head to http://openhumans.org/direct-sharing/projects/manage to create an OAuth2 project in Open Humans. If you do not yet have an Open Humans account, you will need to create one first.

1. Click the button to `Create a new OAuth2 data request project`
  ![](https://cl.ly/0J0s3w1y3R2b/Image%202018-02-15%20at%204.53.51%20PM.png)
2. Fill out the form for your project description. All of this information can be edited later, so don't worry if you aren't sure about it all just yet. However do make sure you fill out the following fields:
    - **Description of data you plan to upload to member accounts** - if you leave this field blank, Open Humans will assume that your project doesn't plan to add data
    - **Enrollment URL** - set this to `http://127.0.0.1:5000`, this should then automatically set the redirect URL to `http://127.0.0.1:5000/complete`

When you have created the project, you'll be able to click on its name in the `project management page` to show its information. From here, get the `activity page`, `client ID`, and `client secret` and set them in your `.env` file. The ID and secret identify and authorize your app. They are used for user authorization and data management.

*Keep your client secret private*, it should not be committed to a repository. In Heroku it will be kept private as an environment variable, and locally it will be available from the `.env` file which should not be committed to git.

## Final steps of app setup

Finally we need to initialize the database and static assets to be able to get the app running. Django will use [SQLite3](http://www.sqlite.org) by default if you do not specify a `DATABASE_URL` in `.env`. For more information on databases you can check out the [Django docs](http://docs.djangoproject.com/en/2.0/ref/databases).

In the main project directory, run the `migrate` command followed by `collectstatic` as follows:

`$ pipenv run python manage.py migrate`

`$ pipenv run python manage.py collectstatic`


Now we are ready to run the app locally. Enter the command `$ pipenv run heroku local`, and don't worry if you see the following warning:

 > warnings.warn('Using settings.DEBUG leads to a memory leak, never')

If you are curious, the cause of this warning is outlined [here](http://stackoverflow.com/questions/4806314/disable-django-debugging-for-celery).

Now head over to http://127.0.0.1:5000 in your browser to see your app running locally. It should look like this:

![](https://cl.ly/1J3X35170e0s/Image%202018-02-16%20at%202.35.57%20AM.png)

Now you have your application built and running locally, we'll head over to Heroku where the app will be deployed remotely.

If you have hit any problems so far, please do let us know in [Github issues](http://github.com/OpenHumans/oh-data-source-template/issues) or come and chat with us over at our [Slack channel](http://slackin.openhumans.org).

## Heroku deployment

### Heroku setup

If you don't already have a Heroku account, head to http://www.heroku.com/ to create a free account now. If you are new to app development, you may also want to go through their [getting started with Heroku/Python guide](https://devcenter.heroku.com/articles/getting-started-with-python#introduction) before continuing with your Open Humans app.

### Creating a Heroku application

Make sure you have installed the [Heroku command line interface](https://devcenter.heroku.com/articles/heroku-cli), then, from your terminal, you can log in and create your app with the following commands:

`$ heroku login`

> *you will be asked for your Heroku credentials*

`$ heroku apps:create your-app-name`

If you use Heroku's free default domain, this will be set by the name you choose here, i.e. you will have

`https://your-app-name.herokuapp.com`

### App configuration

In your browser, head over to `http://dashboard.heroku.com/apps` and log in to see the app you just created.

Go to the `Resources` tab, and add the following Add-ons:

1. `Heroku Redis`
2. `Heroku Postgres`

Next go to the `settings` tab and add the environment variables as in the `.env` file.

1. `OPENHUMANS_CLIENT_ID`
2. `OPENHUMANS_CLIENT_SECRET`
3. `OPEHUMANS_ACTIVITY_PAGE`
4. `DEBUG` = true when needed
5. `REMOTE` = true

Head back over to your terminal and run the following command to initialize and update your code remotely in Heroku:

`$ git push heroku master`

You can watch logs with the command `$ heroku logs -t`.

If you make changes you may have to migrate again, to do this run:

`$ heroku run python manage.py makemigrations`
`$ heroku run python manage.py migrate`
`$ git push heroku master`


## Next steps

### Under the hood

Before starting to edit the code in this demo to create your own project, it may be useful to understand what the existing code is doing.

- Upon arrival at the app, the user sees the homepage (the `index.html` file), on this page is a button which transfers the user to Open Humans for authorization
- The user logs in to their Open Humans account, and clicks to authorize the app to add data, this directs them back to the `complete.html` file
- The `complete` function in the file `views.py` receives a code from Open Humans, exchanges it for a token, and uses this token to retrieve the project member ID which is stored in the `OpenHumansMember` model
- As this page is loaded, an automatic, asynchronous data upload to Open Humans is triggered via the method `xfer_to_open_humans`
  - `xfer_to_open_humans` takes the member ID (which was retrieved during authentication over at the Open Humans site), and runs the method `add_data_to_open_humans`
  - `add_data_to_open_humans` runs with three steps:
    - creates a dummy data file, for demo purposes only (using `make_example_datafile` method)
    - deletes any previous files uploaded with this name (using `delete_oh_file_by_name` method)
    - takes the file path, metadata, and user ID, and uploads to Open Humans (using `upload_file_to_oh` method)
  - `upload_file_to_oh` performs the following steps:
    - gets S3 target for storage
    - performs data upload to this target
    - notifies when the upload is complete

#### Asynchronosity

The `celery.py` file sets up asynchronous tasks for the app. The function `xfer_to_open_humans` in `tasks.py` is called (from `complete` function in `views.py`) asynchronously, by the presence of `.delay` in the function call:

>         xfer_to_open_humans.delay(oh_id=oh_member.oh_id)

Sometimes uploads can take a long time so we advise using the delay so that this does not prevent the app from processing other events. However if you wish to run your app without asynchronosity, you can simply remove the `.delay` component from this function call.

#### Rate limiting

External APIs will often limit how much data you are allowed to fetch per unit time. This template uses the `requests-respectful` package to easily set rate limits when making requests. The requester can be set up as follows

- find out the limitations of the external API by looking at their documentation
- specify the limitations in a realm, found in [`demotemplate/settings.py`](https://github.com/OpenHumans/oh-data-demo-template/blob/master/demotemplate/settings.py#L73)
- when making your request, use the function `make_request_respectful_get` in [`datauploader/tasks.py`](https://github.com/OpenHumans/oh-data-demo-template/blob/a9acbc12d26726dff25a5cd3d583a509d200bedb/datauploader/tasks.py#L154)

## Editing the template

Now you have worked through to create a working demo, and should understand roughly how the demo works, you are ready to customise the code to create your own Open Humans data source. Use the code you have in this repository as a template for your app.

You are likely to want to start making changes in the `tasks.py` file, which is where much of the logic is stored. Instead of generating a dummy data file you will want to think about how to get your own data into the app, whether it is a previously downloaded file, which needs to be processed and/or vetted by the app, or you are working from an external API.

Good luck, and please do [get in touch]((http://github.com/OpenHumans/oh-data-source-template/issues)) to ask questions, give suggestions, or join in with our [community chat](http://slackin.openhumans.org)!
