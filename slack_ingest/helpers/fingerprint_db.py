import json
import os

import boto3
import settings
import sqlalchemy

# # ENDPOINT="postgresmydb.123456789012.us-east-1.rds.amazonaws.com"
# FINGERPRINTDB_HOST = "fingerprint-ecs-staging-db.cft2w19swhah.eu-west-1.rds.amazonaws.com"
# FINGERPRINTDB_PORT = "5432"
# FINGERPRINTDB_USR = "iamuser"
# FINGERPRINTDB_REGION = "eu-west-1"
# FINGERPRINTDB_DBNAME = "fingerprintdb"


def get_conn():
    client = boto3.client("rds")

    token = client.generate_db_auth_token(
        DBHostname=settings.FINGERPRINTDB_HOST,
        Port=settings.FINGERPRINTDB_PORT,
        DBUsername=settings.FINGERPRINTDB_USER,
        Region=settings.FINGERPRINTDB_REGION,
    )
    database_url = sqlalchemy.engine.url.URL(
        drivername="postgresql+psycopg2",
        username=settings.FINGERPRINTDB_USER,
        password=token,
        host=settings.FINGERPRINTDB_HOST,
        port=settings.FINGERPRINTDB_PORT,
        database=settings.FINGERPRINTDB_DBNAME,
    )
    engine = sqlalchemy.create_engine(database_url)
    conn = engine.connect()
    return conn


def local_get_fingerprint_users():
    local_users_json = """
    {
"UPG9G6D38": {
    "firm_name": "IP Sentinel",
    "firm_identifier": "ips",
    "assignment_name": "",
    "first_name": "James",
    "last_name": "TEST Hogbin",
    "email": "james@fingerprint-supervision.com",
    "slack_id": "UPG9G6D38"
  }
}
    """
    return json.loads(local_users_json)


def get_fingerprint_users_for_client(client_name: str) -> dict:
    if (
        os.getenv("AWS_EXECUTION_ENV", None) is None or os.getenv("CIBUILD", None) == "1"
    ):  # This is local exec or CICD build. Only Lambdas have access to RDS dbs.
        return local_get_fingerprint_users()
    sql = sqlalchemy.text(
        """SELECT ff.firm_name, ff.firm_identifier, ffa.assignment_name,
                              -- ffa.fingerprint_user_id,
                              fu.first_name, fu.last_name, fu.email, fu.slack_id
        from main_fingerprintfirm ff, main_fingerprintfirmassignment ffa, main_fingerprintuser fu
        where ff.id = ffa.fingerprint_firm_id and
              ffa.fingerprint_user_id = fu.id and
              ff.firm_identifier = :firm_identifier
              and fu.slack_id is not null"""
    )

    out = {}
    with get_conn() as conn:
        res = conn.execute(sql, firm_identifier=client_name)
        i = 0
        for row in res:
            if i <= 10:
                print(row)
                i += 1
            out[row["slack_id"]] = row

    # TODO delete
    print("DEBUG Connected to DB for fingerprint users!")
    # print(out)
    return out
