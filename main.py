from flask import Flask, jsonify, request
import boto3
import config

app = Flask(__name__)

@app.route('/ec2/list', methods=['GET'])
def list_instances():
    credentials = parse_credentials_for_listing(request.args)
    ec2 = create_boto3_client(*credentials)
    id_list = get_instance_ids(ec2)
    return jsonify(instances=id_list)

@app.route('/ec2/start', methods=['POST'])
def start_instance():
    *credentials, instance_id = parse_credentials_for_start_stop(request.args)
    ec2 = create_boto3_client(*credentials)
    state = start_instance(ec2, instance_id)
    state['InstanceId'] = instance_id
    return jsonify(state)

@app.route('/ec2/stop', methods=['POST'])
def stop_instance():
    *credentials, instance_id = parse_credentials_for_start_stop(request.args)
    ec2 = create_boto3_client(*credentials)
    state = stop_instance(ec2, instance_id)
    state['InstanceId'] = instance_id
    return jsonify(state)


def stop_instance(ec2, instance_id):
    response = ec2.stop_instances(
        InstanceIds=[instance_id]
    )
    state = response['StoppingInstances'][0]['CurrentState']
    return state


def start_instance(ec2, instance_id):
    response = ec2.start_instances(
        InstanceIds=[instance_id]
    )
    state = response['StartingInstances'][0]['CurrentState']
    return state


def parse_credentials_for_listing(args):
    return (
        args.get('aws_access_key_id'),
        args.get('aws_secret_access_key'),
        args.get('region_name')
    )

def parse_credentials_for_start_stop(args):
    return (
        args.get('aws_access_key_id'),
        args.get('aws_secret_access_key'),
        args.get('region_name'),
        args.get('InstanceId')
    )


def create_boto3_client(aws_access_key_id, aws_secret_access_key, region_name):
    return boto3.client(
        'ec2',
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=region_name
    )

def get_instance_ids(ec2):
    response = ec2.describe_instances()
    instance_ids = []
    reservations = response["Reservations"]
    for reservation in reservations:
        instances = reservation["Instances"]
        for instance in instances:
            instance_id = instance["InstanceId"]
            instance_ids.append(instance_id)
    return instance_ids

if __name__ == '__main__':
    app.run(
        host=config.host,
        port=config.port,
        debug=config.debug
    )
