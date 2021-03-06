# flask-api-structure

This project is designed for developing RESTful API with `Flask`.

## Quick Start

1. Install Python dependencies.
    ```sh
    pip install -r requirements.txt
    ```
2. `flask run`

## Database

1. Creating the migration repository.
    ```
    $ flask db init
    ```

2. Database Migration.
    ```
    $ flask db migrate -m "users table"
    ```
    The comment given with the `-m` option is optional, it adds a short descriptive text to the migration.

    The `flask db migrate` command does not make any changes to the database, it just generates the migration script. To apply the changes to the database, the `flask db upgrade` command must be used.

    ```
    $ flask db upgrade
    ```

    Also it has a `flask db downgrade` command, which undoes the last migration

## Configurations on server.
Follow the steps to run the application on remote server(MS Azure, Ubuntu LTS).
### Installation
1. Install Python dependencies.
    ```sh
    $ pip install -r requirements.txt
    ```
2. Install `flask` with `apt-get`. (This step maybe optional, it depends on whether the `flask` command can run on the terminal or not.)
    ```sh
    $ sudo apt-get install python3-flask
    ```

3. Install `nginx` - a open-sourced HTTP server.
    ```sh
    $ sudo apt-get install nginx
    ```

    Type your domain name or IP address in the browser. It should be a `welcome to nginx` page.

4. Install `gunicorn` with `apt-get`.
Suppose the Flask application can run locally.
    `sudo apt-get install python3-gunicorn`

### Configuration

5. Configure `nginx`.
    - ```$ cd /etc/nginx/sites-enabled/```

        List the current folder, a file named `default` should be listed. Use `vi`/`vim` to open and edit `default` file.
    - ```$ sudo vi default```

        The content should be like:
        ```
        # ......
        server {
            listen 80 default_server;
            listen [::]:80 default_server;
            # ......

            root /var/www/html;
            index index.html index.htm index.nginx-debian.html;

            server_name _;

            location / {
                # First attempt to serve request as file, then
                # as directory, then fall back to displaying a 404.
                try_files $uri $uri/ =404;
            }
            # ......
        }

        ```

    - Modify the `location /` part to following:

        ```
            location / {
                # auth_basic "Administrator's area";
                # auth_basic_user_file /etc/apache2/.htpasswd;
                # First attempt to serve request as file, then
                # as directory, then fall back to displaying a 404.
                # try_files $uri $uri/ =404;
                proxy_pass http://localhost:5000; # <- Mind the port that th e flask app is using.
            }
        ```

        **NOTE: Save the changes**

    - After the configuration is done, restart the `nginx`.

        *You can use `nginx -t` to test the configuration first.*
        ```sh
        $ sudo service nginx restart
        ```
    
    
6. Use `gunicorn`.

    **WSGI** servers provide the interface between an HTTP server and application/framework(Flask, etc.). HTTP requests are received by a HTTP server such as Nginx and passed along to WSGI-compliant framework/application such as Flask application.

    **Gunicorn** is a stand-alone **WSGI** web application server which offers a lot of functionality. It natively supports various frameworks with its adapters, making it an extremely easy to use drop-in replacement for many development servers that are used during development.

    ```
    $ gunicorn -b localhost:5000 -w 4 start:app
    ```

    The `-b` option tells gunicorn where to listen for requests, which I set to the internal network interface at port 5000. It is usually a good idea to run Python web applications without external access, and then have a very fast web server that is optimized to serve static files accepting all requests from clients. This fast web server will serve static files directly, and forward any requests intended for the application to the internal server. I will show you how to set up nginx as the public facing server in the next section.

    The `-w` option configures how many workers gunicorn will run. Having four workers allows the application to handle up to four clients concurrently, which for a web application is usually enough to handle a decent amount of clients, since not all of them are constantly requesting content. Depending on the amount of RAM your server has, you may need to adjust the number of workers so that you don't run out of memory.

    The `start:app` argument tells gunicorn how to load the application instance. The name before the colon is the module that contains the application, and the name after the colon is the name of this application.

    While gunicorn is very simple to set up, running the server from the command-line is actually not a good solution for a production server. What I want to do is have the server running in the background, and have it under constant monitoring, because if for any reason the server crashes and exits, I want to make sure a new server is automatically started to take its place. And I also want to make sure that if the machine is rebooted, the server runs automatically upon startup, without me having to log in and start things up myself. I'm going to use the `supervisor` package that I installed above to do this.

7. Use `supervisor`.
    The supervisor utility uses configuration files that tell it what programs to monitor and how to restart them when necessary. Configuration files must be stored in `/etc/supervisor/conf.d`. Here is a configuration file for flask application, which I'm going to call `flask.conf` (The name is not certain):

    `/etc/supervisor/conf.d/flask.conf`
    ```
    [program:applicationName]
    command=/home/project/flask/venv/bin/gunicorn -b localhost:5000 -w 4 start:app
    directory=/home/project/flask
    user=ubuntu
    autostart=true
    autorestart=true
    stopasgroup=true
    killasgroup=true
    ```

    The `command`, `directory` and `user` settings tell supervisor how to run the application. The `autostart` and `autorestart` set up automatic restarts due to the computer starting up, or crashes. The `stopasgroup` and `killasgroup` options ensure that when supervisor needs to stop the application to restart it, it also reaches the child processes of the top-level gunicorn process.

    After you write this configuration file, you have to reload the supervisor service for it to be imported:

    ```sh
    $ sudo supervisorctl reload
    ```

    And just like that, the gunicorn web server should be up and running and monitored!
    ***
    **NOTE: use following command to check the status of the supervisor's process**
    ```sh
    $ sudo supervisorctl status
    ```


***
After all the configuration is done. Every time it needs restart, just simply run following commands:
```sh
$ git pull
$ sudo supervisorctl stop applicationName
$ sudo supervisorctl start applicationName
```

**Mind the last argument is the process name**

## Add basic authorization(Optional)

For a short term of restriction, using basic auth for nginx is an option.

Reference:
    [Restricting Access with HTTP Basic Authentication](https://docs.nginx.com/nginx/admin-guide/security-controls/configuring-http-basic-authentication/)


## Deploy with Docker

1. Build `Docker` image.

    ```sh
    $ docker build -t flask-api-structure:latest .
    ```

    You can obtain a list of the images that you have locally with the `docker images` command.

2. Starting a Container.

    ```sh
    $ docker run --name flask-api-structure -d -p 8000:5000 --rm flask-api-structure:latest
    ```

    The `--name` option provides a name for the new container.
    
    The `-d `option tells Docker to run the container in the background. Without -d the container runs as a foreground application, blocking your command prompt.
    
    The `-p` option maps container ports to host ports. The first port is the port on the host computer, and the one on the right is the port inside the container. The above example exposes port `5000` in the container on port `8000` in the host, so you will access the application on `8000`, even though internally the container is using `5000`.
    
    The `--rm` option will delete the container once it is terminated. While this isn't required, containers that finish or are interrupted are usually not needed anymore, so they can be automatically deleted.
    
    The last argument is the container image name and tag to use for the container.
    
    After you run the above command, you can access the application at http://localhost:8000.


    If you want to see what containers are running, you can use the `docker ps` command:
    ```
    $ docker ps
    ```

    ***
    There is also a need to have run-time environment variables that can be set via the docker run command, and for these variables, the `-e` option can be used. The following example sets a secret key and sends email through a gmail account:

    ```
    $ docker run --name flask-api-structure -d -p 8000:5000 --rm -e SECRET_KEY=my-secret-key \
        -e MAIL_SERVER=smtp.googlemail.com -e MAIL_PORT=587 -e MAIL_USE_TLS=true \
        -e MAIL_USERNAME=<your-gmail-username> -e MAIL_PASSWORD=<your-gmail-password> \
        flask-api-structure:latest
    ```

## References

[The Flask Mega-Tutorial Part XVII: Deployment on Linux](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-xvii-deployment-on-linux)

[How to properly host Flask application with Nginx and Guincorn](https://www.e-tinkers.com/2018/08/how-to-properly-host-flask-application-with-nginx-and-guincorn/)

