1. Guest user on Rabbit MQ is deleted for security reasons, so make your own user and add permissions as directed here 
[https://www.cherryservers.com/blog/how-to-install-and-start-using-rabbitmq-on-ubuntu-22-04](https://www.cherryservers.com/blog/how-to-install-and-start-using-rabbitmq-on-ubuntu-22-04) You can check the available users using:

```
rabbitmqctl list_users
```


2. Default virtual host deleted using 

```rabbitmqctl delete_vhost /
```

3. 