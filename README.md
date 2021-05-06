# Speedo, 

Speedo is a lightweight python client library and server
(fastAPI+sqlalchemy).

The database is created via [Object Relational Mappers (SQLAlchemy
ORM)](https://docs.sqlalchemy.org/en/14/orm/) using either :
- **sqlite** (in-memory mode) for **development**
- **postgresql** for **production**

In production, [alembic](https://alembic.sqlalchemy.org/en/latest/) is
a lightweight database migration tool for versioning the releases.

## Docs

A simple Live OpenAPI documentation can be found under _<url>/docs_ or
_<url>/redoc_.

## Use Speedo's client and server
You can directly use Speedo services via the [nokxpkgs](https://github.com/nokx5/nokxpkgs#add-nokxpkgs-to-your-nix-channel) channel.
```
# you can avoid this export by adding nokxpkgs to your channels
export NIX_PATH=nokxpkgs=https://github.com/nokx5/nokxpkgs/archive/main.tar.gz
```

* use speedo server

    1. import speedo with a nix-shell
        ```
        nix-shell -I nixpkgs=$PWD --pure -p speedo
        ```

    2. execute it
        ```
        speedo
        ```

* use speedo client

    1. import speedo_client with a nix-shell
        ```
        nix-shell -I nixpkgs=$PWD --pure -p python3Packages.speedo_client
        ```

    2. enter python and import the library
        ```
        import speedo_client
        ```

## Develop Speedo Services
### Develop using the nix shell
1. to enter the nix-shell, you have to explicitly call the ```default.nix``` file.
    ```
    nix-shell --pure -A dev
    ```

2. check python requirements if you are skeptic about nix.

    ```
    pip install -r requirements_client.txt
    pip install -r requirements_server.txt
    ```

3. check that the ```PYTHONPATH``` is correctly set.
    ```
    export PYTHONPATH=$PWD:$PYTHONPATH
    export DEBUG_SPEEDO_SQL="ENABLED"  # for sql debug info
    ```

4. select the database

    * run explicitly a postgresql database and use it
        ```
        export PGHOST="$PWD/scripts/localdb/sockets"
        export PGDATA="$PWD/scripts/localdb/pgdata"
        export PGPORT="5432"
        export PGDATABASE="speedoDB"
        export PGUSER="$USER"
        export PGPASS=""
        # example of execution
        trap "$PWD/scripts/rundb_postgresql remove" EXIT
        $PWD/scripts/rundb_postgresql add
        ```
        From there you can check if the database is accessible.
        ```
        # list tables
        psql --host $PGHOST -U $PGUSER -p $PGPORT -d $PGDATABASE -c '\d'
        # list the rows of a selected table
        psql --host $PGHOST -U $PGUSER -p $PGPORT -d $PGDATABASE -c 'SELECT * FROM spd_user;'
        ```
        In case postgresql didn't clean the database properly.
        ```
        rm -rf nix/{log,pgdata,pids,sockets}
        ```

    * run sqlite in-memory
        ```
        unset PGHOST
        ```

5. run the tests
    ```
    pytest
    ```

6. start a server using [uvicorn](https://www.uvicorn.org/) and visit the urls http://127.0.0.1:8000/docs and http://127.0.0.1:8000/redoc.
    ```
    ./scripts/speedo
    ```

7. close the nix-shell ;-)

8. *Optional*, create a docker image
    ```
    nix-build -A speedo-docker-image
    docker load < result
    docker run -it speedo:dev
    # look for the right IPAddress
    docker inspect <CONTAINER_ID> | grep IPAddress
    ```

**Congratulation!**

You have now all the tools to develop Speedo!

## Comment on [Alembic](https://alembic.sqlalchemy.org/en/latest), docker and staging to production
If you never run alembic before and you have never created modification to the database before, you can execute alembic for the first time.
```
alembic revision --autogenerate
```

## Deployment

### Dev Deployment
Feel free to work

### Staging Deployment
Open a ticket of the form

### Production Deployment
Open a ticket of the form


### What does Autogenerate Detect (and what does it not detect?)

The vast majority of user issues with Alembic centers on the topic of
what kinds of changes autogenerate can and cannot detect reliably, as
well as how it renders Python code for what it does detect. **It is
critical to note that autogenerate is not intended to be perfect. It
is always necessary to manually review and correct the candidate
migrations that autogenerate produces.** The feature is getting more and
more comprehensive and error-free as releases continue, but one should
take note of the current limitations.


### DB Migration with [Alembic](https://alembic.sqlalchemy.org/en/latest)
After setting your alembic for the first time or if you want to
integrate your modifications to the database (see ```schemas.py```),
you will need to update alembic.
```
alembic upgrade head
```
Once you did this step you can pytest the project or execute the web
interface of fastapi.

### DB Migrations with Alembic:

-   modify your models in models.py
-   run `alembic revision --autogenerate`
-   check the newest file under ./alembic/versions is correct
-   run `alembic upgrade head`

# Use the speedo_client
You should add the following nix recipes in order to test your code with the associate patch or mock.
```
buildInputs = [speedo_client];
checkBuildInputs = [speedo mock requests];
```
you could then use 
```
from speedo_client.mock_client import MockSpeedoClient
```
to mock or patch the speedo_client.
