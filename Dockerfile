FROM public.ecr.aws/lambda/python:3.8


COPY . ./
RUN pip install -r requirements.txt

# Hack to get latest boto3 for newest APIs
RUN pip install boto3 -t .


CMD ["handler.s3_proxy_handler"]