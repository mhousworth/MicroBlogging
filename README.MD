# MicroBlogging

A set of web services implemented with [Bottle].

### Includes:
- SQLite databases and services for user information and timeline posts
- Local Amazon DynamoDB for direct messaging service
- Redis for a posts search engine service

### SETUP:
##### Create databases with the commands below
```
$ sqlite3 users.db < users.sql
$ sqlite3 posts.db < posts.sql
```
##### Setting up dynamodb database
Installation:
```
$ sudo apt update
$ sudo apt install --yes awscli
```
Run with:

`$ java -Djava.library.path=./DynamoDBLocal_lib -jar DynamoDBLocal.jar -sharedDb`

Configure with:

`$ aws configure`
```
AWS Access Key ID [None]: fakeMyKeyId
AWS Secret Access Key [None]: fakeSecretAccessKey
Default region name [None]: us-west-2
Default output format [None]: table
```

Populate messages table:

`$ python3 messageInitDb.py`

##### Ensure Redis is installed and running
`$ redis ping`
##### Otherwise install redis and python packages
```
$ sudo apt update
$ sudo apt install --yes redis
$ sudo apt install --yes python3-hiredis
```

### Start services with the following command
```
$ foreman start -m gateway=1,userService=1,timelineService=3,messageService=1,searchEngineService=1
```

##### Add sample posts (optional)
`$ python3 samplePosts.py`

[Bottle]: https://bottlepy.org/docs/0.12/
