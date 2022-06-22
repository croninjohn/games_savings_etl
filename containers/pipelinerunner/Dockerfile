FROM python:3.9.5

WORKDIR /code
ENV PYTHONPATH=/code/src

# install cron
RUN apt-get update && apt-get install cron -y

ADD ./containers/pipelinerunner/requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY ./ /code/

# Copy cron job file file to the cron.d directory
COPY /scheduler/etl_cron_runner /etc/cron.d/etl_cron_runner
 
# Give execution rights on the cron job
RUN chmod 0644 /etc/cron.d/etl_cron_runner

# Apply cron job
RUN crontab /etc/cron.d/etl_cron_runner

# Create the log file to be able to run tail
RUN touch /var/log/cron.log
 
# Run cron
CMD cron && tail -f /var/log/cron.log