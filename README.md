# Anonymize Data with S3 Object Lambda and Gretel Transforms

This repo demonstrates how to launch a simple AWS stack that anonymizes S3 object data at access time using S3 Object Lambdas.

Components:

- `handler.py`- the core business logic that builds a Gretel Transform Pipeline and Lambda handlers for an API endpoint and the actual S3 object transformer.
- `Dockerfile` - builds the container that AWS Lambda will use
- `serverless.yml` - a Serverless config that launches a full AWS CloudFormation Stack that implements our solution.


For demonstration purposes, we use some public mock data, which is in the `2021-03-22.csv` file. This file will need to be uploaded to the S3 bucket created by the stack.

**Local Testing**:

The AWS managed container comes with the Lambda runtime emulator, so we can test our core business logic locally:

```
$ docker build -t gretel-transform-test .
$ docker run -it -p 9000:8080 gretel-transform-test "handler.record_handler"
$ python test_local.py
```


**Deploy with Severless**:

In `serverless.yml`, update `custom.baseName` to something different that won't
cause S3 bucket naming conflicts.

```
$ npm install serverless
$ sls deploy
```

You'll need to upload the sample CSV data to the bucket that gets created.

When you get back the endpoints from the `Service Information` output, you should be able to issue a `GET /dev/share?key=2021-03-22.csv`.