# Transform S3 Objects with Gretel Open Source Transforms

See the blog here: TODO

**Local Testing**:

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

When you get back the endpoints from the `Service Information` output, you could be able to issue a `GET /dev/share?key=2021-03-22.csv`.