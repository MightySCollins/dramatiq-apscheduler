# Dramatiq ApScheduler
Allows simple command line usage of ApScheduler to add tasks directly to Dramatiq. It is designed to support multiple concurrent scheduler process such as in the case of Elastic Beanstalk.

You can run multiple process and each one will check if it's the leader before executing any tasks.

## Config
Below is a minimal example of the config.
 
```yaml
config:
  redis: redis://localhost/
jobs:
  trigger_feed_run_every_10_minutes:
    func: run_feeds
    crontab: "*/10 * * * *"
```

### Triggers
Currently only one trigger is supported `crontab`. We recommend you use https://crontab.guru/ to validate your expressions.

## Usage
Just run the task to start the process. You can also add the `--debug` flag to get extra logging.

    dramatiq_apscheduler config.yaml