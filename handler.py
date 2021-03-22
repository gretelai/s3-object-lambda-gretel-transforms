"""
Example AWS Lambda Handler for transforming
records with Gretel Open Source Transforms.
"""
import io
import sys
import json
from pathlib import Path
import os

import pandas as pd
import requests

from gretel_client.transformers import (
    DateShiftConfig,
    RedactWithCharConfig,
    FakeConstantConfig,
    DataTransformPipeline,
    DataPath,
    FieldRef,
    StringMask,
)

# Hack to get the latest version of boto3
sys.path.insert(0, Path(__file__).parent.as_posix())


# Build a simple transform pipeline for our records
# - replace name with a fake name
# - redact parts of employee id
# - date shift the following fields:
#   - DOB
#   - DateofHire
# - fake manager name


# Shift dates by +/- 10 days. Also ensure dates are consistently shifted
# based on the employee name
date_shifter = DateShiftConfig(
    secret="2B7E151628AED2A6ABF7158809CF4F3CEF4359D8D580AA4F7F036D6F04FC6A95",
    lower_range_days=-10,
    upper_range_days=10,
    date_format="%m/%d/%Y",
    tweak=FieldRef("Employee_Name"),
)

name_replacer = FakeConstantConfig(seed=8675309, fake_method="name")

# Mask up until the last 4 chars
id_redactor = RedactWithCharConfig(
    mask=[StringMask(end_pos=-4)]
)


paths = [
    DataPath(input="*Name", xforms=[name_replacer]),
    DataPath(input="DOB", xforms=[date_shifter]),
    DataPath(input="DateofHire", xforms=[date_shifter]),
    DataPath(input="EmpID", xforms=[id_redactor]),
    # Uncomment to allow all other fields to pass through
    # DataPath(input="*")
]

pipeline = DataTransformPipeline(data_paths=paths)


def _transform_data(data: str) -> str:
    """Take the full CSV data, load to a DataFrame,
    transform and return the new version.
    """
    df = pd.read_csv(io.StringIO(data))
    xf_df = pipeline.transform_df(df)
    out_str = io.StringIO()
    xf_df.to_csv(out_str, index=False)
    return out_str.getvalue()


def s3_proxy_handler(event: dict, context):
    """Handler for the S3 object transform Lambda
    """
    import boto3
    client = boto3.client("s3")
    object_get_context = event["getObjectContext"]
    request_route = object_get_context["outputRoute"]
    request_token = object_get_context["outputToken"]
    s3_url = object_get_context["inputS3Url"]
    resp = requests.get(s3_url)

    if resp.status_code != 200:
        client.write_get_object_response(
            StatusCode=resp.status_code,
            RequestRoute=request_route,
            RequestToken=request_token
        )
        return {"status_code": 200}

    source_data_str = resp.content.decode("utf-8")
    transformed_data_str = _transform_data(source_data_str)

    client.write_get_object_response(
        Body=transformed_data_str,
        RequestRoute=request_route,
        RequestToken=request_token
    )

    return {"status_code": 200}


def get_sharing_url(event: dict, context):
    """Handler for the REST API call.  Generate a pre-signed S3 URL
    to do a GetObject on the S3 Object Lambda Access Point. Utilize
    the ``key`` query param to make this a dynamic request.
    """
    import boto3
    from botocore.config import Config
    client = boto3.client("s3", config=Config(signature_version="s3v4"))
    key = event.get("queryStringParameters", {}).get("key", None)
    if not key:
        return {
            "statusCode": 400,
            "body": json.dumps({"message": "key required"})
        }
    url = client.generate_presigned_url(
        "get_object",
        Params={
            "Bucket": os.getenv("OLAP_BUCKET"),  # noqa
            "Key": key
        }
    )

    return {
        "statusCode": 200,
        "body": json.dumps({"url": url})
    }


def record_handler(event: dict, context):
    """For testing the container locally
    """
    _transformed = _transform_data(event["data"])
    return {"data": _transformed}
