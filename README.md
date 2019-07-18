# Dramatiq ApScheduler
Allows simple command line usage of ApScheduler to add tasks directly to Dramatiq. It is designed to support multiple concurrent scheduler process such as in the case of Elastic Beanstalk.

You can run multiple process and each one will check if it's the leader before executing any tasks.

## Requirements
The application uses rabbitmq and redis.

By default both rabbitmq and redis will just use localhost but on most systems you are running these services on another server. You can configure both redis and rabbitmq by providing the connection urls as options `redis` and `rabbitmq` or environment variables `SCHEDULE_REDIS` and `SCHEDULE_RABBITMQ`.

## Config
Below is a minimal example of the config. To add more tasks just simply edit the `jobs` config option.  
 
```yaml
jobs:
  trigger_feed_run_every_10_minutes:
    func: run_feeds
    crontab: "*/10 * * * *"
  trigger_test_task:
    func: test_task
    crontab: "*/1 * * * *"
    queue_name: test

```

### Triggers
Currently only one trigger is supported `crontab`. We recommend you use https://crontab.guru/ to validate your expressions.

## Usage
Just run the task to start the process. You can also add the `--debug` flag to get extra logging.

```
Usage: dramatiq_apscheduler [OPTIONS] CONFIGFILE

Options:
  --debug           Enables debug logging
  --rabbitmq TEXT   rabbitmq connection url: amqp://127.0.0.1:5672/
  --redis TEXT      redis connection url: redis://localhost/
  --sticky INTEGER  How long a process should stay the leader
  --help            Show this message and exit.
```

You can run with the demo config:

    dramatiq_apscheduler config.yaml
    
## Development
The easiest way to develop this application is in a venv. You can see more details in the [click documentation](https://click.palletsprojects.com/en/7.x/setuptools/) but if your venv is setup just run the below command.
 
     pip install --editable .

## Dockerfile
A docker image is also provided which allows you to easily run the application anywhere.

    docker pull scollins/dramatiq-apscheduler
    docker run scollins/dramatiq-apscheduler