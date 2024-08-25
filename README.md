# tyrion
Tyrion URL Shortener written in Python which uses FastAPI and DynamoDB

## Installation
1. Clone the repository. `git clone git@github.com:uniacco-tech/tyrion.git`
2. Go to the project directory. `cd tyrion`
3. Create a virtual environment. `python3 -m venv venv`
4. Activate the virtual environment. `source venv/bin/activate`
5. Install the dependencies. `pip install -r requirements.txt --no-cache-dir --upgrade`
6. Run the server. `uvicorn main:app --reload --port 8004`
7. Setup dynamodb locally. [Docs](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/DynamoDBLocal.DownloadingAndRunning.html)
8. Run the following command to start dynamodb locally.
```bash
java -Djava.library.path=./DynamoDBLocal_lib -jar DynamoDBLocal.jar -sharedDb -port 8005
```
9. Create a table named `tyrion` with `short_url` as hash key.
```python
import os

import boto3
from dotenv import load_dotenv


load_dotenv()

db_url =  os.getenv('DB_URL')
region_name = os.getenv('DB_REGION')
db_table = os.getenv('DB_TABLE')

dynamodb = boto3.resource(
    service_name='dynamodb',
    endpoint_url=db_url,
    region_name=region_name,
)

table = dynamodb.create_table(
    TableName=db_table,
    KeySchema=[
        {'AttributeName': 'short_code', 'KeyType': 'HASH'},
    ],
    AttributeDefinitions=[
        {'AttributeName': 'short_code', 'AttributeType': 'S'},
    ],
    ProvisionedThroughput={
        'ReadCapacityUnits': 5,
        'WriteCapacityUnits': 5
    },
)
dynamodb.meta.client.get_waiter('table_exists').wait(TableName=db_table)
print(f'Created table {db_table}')
```
---

## API Documentation
[Postman Docs](/docs/collections/Tyrion.postman_collection.json)

---

## Configurations
[App Server: Gunicorn Service File](/docs/config/tyrion.service)

[Web Server: Nginx Config](/docs/config/tyrion.conf)

---

## Deployment
1. Go to [AWS Console](https://ap-south-1.console.aws.amazon.com/ec2/home?region=ap-south-1#Instances:tag:Name=url-shortner;v=3;$case=tags:true%5C,client:false;$regex=tags:false%5C,client:false) and connect to `url-shortner` instance.
2. Go to project directory. `cd ~/tyrion`
3. Pull the latest changes. `git pull origin master`
4. Activate the virtual environment. `source venv/bin/activate`
5. Install the dependencies. `pip install -r requirements.txt --no-cache-dir --upgrade`
6. Restart the server. `sudo systemctl restart tyrion`
7. Verify logs. `tail -f /var/log/tyrion/app.log`
