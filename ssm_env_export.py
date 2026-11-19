#!/usr/bin/env python3

import argparse
import boto3

def fetch_parameters(ssm_path: str):
    """Fetch all parameters under the namespace."""
    session = boto3.session.Session()
    client = session.client("ssm")

    paginator = client.get_paginator('get_parameters_by_path')
    iterator = paginator.paginate(
        Path=ssm_path,
        Recursive=False,
        WithDecryption=True,
        PaginationConfig={'PageSize': 10}
    )

    params = {}

    for page in iterator:
        for param in page.get("Parameters", []):
            name = param["Name"].split("/")[-1]  # Last path segment
            value = param["Value"]
            params[name] = value

    return params

def write_env_file(env_vars: dict, outfile: str):
    """Write the parameters as KEY="VALUE" lines."""
    with open(outfile, "w") as f:
        for key, value in env_vars.items():
            safe_value = value
            safe_value = safe_value.replace("\\", "\\\\")   # Escape backslashes
            safe_value = safe_value.replace('"', '\\"')     # Escape quotes
            safe_value = safe_value.replace("\n", "\\n")    # Escape newlines
            f.write(f'{key}="{safe_value}"\n')

def main():
    parser = argparse.ArgumentParser(
        description="Fetch all SSM params from a namespace and generate a .env file"
    )
    parser.add_argument("ssm_path", help="Root SSM namespace (e.g. /prod/api/)")
    parser.add_argument("output_file", help="Output .env filename")

    args = parser.parse_args()

    print(f"Fetching SSM parameters from: {args.ssm_path}")
    params = fetch_parameters(args.ssm_path)

    if not params:
        print("No parameters found in SSM path -> creating empty .env file.")
        open(args.output_file, "w").close()
        print(f"Created empty {args.output_file}")
        return 0

    print(f"Writing {len(params)} variables to {args.output_file}")
    write_env_file(params, args.output_file)

    print("Done! .env file generated successfully.")


if __name__ == "__main__":
    main()
