# docker-compose-watch

Watch and stop, rebuild and start docker-compose services on filesystem changes

```
$ docker-compose-watch -h
Usage: docker-compose-watch [opts]
    -f, --file FILE            Alternate docker compose file
    -i, --ignore PATTERN       Specify patterns to ignore
    -o, --only PATTERN         Specify patterns to watch
    -h, --help                 Show this help listing
    
    
$ docker-compose-watch -f 2.yml -o '*.py' &
[1] 53153
Building coordinator
Step 1 : FROM python:3.5.2-onbuild
# Executing 3 build triggers...
Step 1 : COPY requirements.txt /usr/src/app/
 ---> Using cache
Step 1 : RUN pip install --no-cache-dir -r requirements.txt
 ---> Using cache
Step 1 : COPY . /usr/src/app
 ---> Using cache
 ---> 3272b091f095
Step 2 : CMD python -u server.py
 ---> Using cache
 ---> 2a2cb0977c75
Successfully built 2a2cb0977c75
WARNING: Found orphan containers (ft_rethinkdb_1) for this project. If you removed or renamed this service in your compose file, you can run this command with the --remove-orphans flag to clean it up.
ft_coordinator_1 is up-to-date
Attaching to ft_coordinator_1
coordinator_1  | about to connect
$ touch/coordinator.py # <------- CHANGING A FILE!!!
$ Going to remove ft_coordinator_1
Removing ft_coordinator_1 ... done
Building coordinator
Step 1 : FROM python:3.5.2-onbuild
# Executing 3 build triggers...
Step 1 : COPY requirements.txt /usr/src/app/
 ---> Using cache
Step 1 : RUN pip install --no-cache-dir -r requirements.txt
 ---> Using cache
Step 1 : COPY . /usr/src/app
 ---> Using cache
 ---> 3272b091f095
Step 2 : CMD python -u server.py
 ---> Using cache
 ---> 2a2cb0977c75
Successfully built 2a2cb0977c75
WARNING: Found orphan containers (ft_rethinkdb_1) for this project. If you removed or renamed this service in your compose file, you can run this command with the --remove-orphans flag to clean it up.
Creating ft_coordinator_1
coordinator_1  | about to connect
```
