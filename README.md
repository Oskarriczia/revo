# Revo Birthday App

# Quickstart

run

`make run`

then interact with the app

`curl -v -H 'Content-Type: application/json' -X PUT localhost:7777/hello/john -d '{ "dateOfBirth": "1985-11-1" }'`

```
* Host localhost:7777 was resolved.
* IPv6: ::1
* IPv4: 127.0.0.1
*   Trying [::1]:7777...
* Connected to localhost (::1) port 7777
> PUT /hello/john HTTP/1.1
> Host: localhost:7777
> User-Agent: curl/8.7.1
> Accept: */*
> Content-Type: application/json
> Content-Length: 30
>
* upload completely sent off: 30 bytes
< HTTP/1.1 204 NO CONTENT
< Server: Werkzeug/3.1.3 Python/3.13.3
< Date: Tue, 22 Apr 2025 19:21:01 GMT
< Content-Type: text/html; charset=utf-8
< Connection: close
<
* Closing connection
```

`curl localhost:7777/hello/john`

```
{
  "message": "Hello, john! Your birthday is in 193 day(s)"
}
```

## Preface

### What and why
There is at least dozen different ways to write, deploy and productionalize a simple app like this.
Serverless Lambda (or similar), Beanstalk, App Engine, raw server/vm deployment, k8s, etc.
All of these are fine, but suitable for different applications and come with their own pros and cons.
Managed services usualy allows you to get in your code fast, but they lock you in big time.

In this scenario, k8s deployment as a helm chart has been used.
It's the most straight forward scenario to productionalize, it's portable, highly customizable and vendor agnostic.
Given that, the database in question is postgres, zalando postgresql operator with a simple cluster is recommended.

Providing a reliable k8s cluster with storage, network, ingress, etc might require some work, but will benefit the organization long term.
Hopefully, a running cluster, available for dev workloads is somewhere out there, ready to be used.

CI/CD and remote deployment is not yet fully supported as it requires remote artifact store.


## Deploying locally

### Prerequisites

* docker
* make (not strictly necessary, but useful)

# Install

### values.yaml

Look at the `values.yaml` and create your own file with proper overrides. 
