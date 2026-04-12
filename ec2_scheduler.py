import boto3
ec2_client = boto3.client('ec2', region_name='us-east-1')

def lambda_handler(event, context):
        
    action = event.get("action")
    response = ec2_client.describe_instances(
        Filters = [
        {
            'Name': 'tag:AutoSchedule',
            'Values': ['True']
        },
        {
            'Name': 'tag:Environment',
            'Values': ['Dev']
        }
      ]
    )    
    instance_ids = []

    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            instance_ids.append(instance['InstanceId'])

    print(f"Scheduled Instances: {instance_ids}")

    # Start or Stop Instances based on the action
    if instance_ids:
        if action == "start":
            print(f"Starting Instances: {instance_ids} ...")
            ec2_client.start_instances(
                InstanceIds=instance_ids
                )
        elif action == "stop":
            print(f"Stopping Instances: {instance_ids} ...")
            ec2_client.stop_instances(
                InstanceIds=instance_ids
                )
        print(f"{action.upper()} action triggered for {len(instance_ids)} instances")
        

            
            