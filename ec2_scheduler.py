import boto3
import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

ec2_client = boto3.client('ec2')


def lambda_handler(event, context):
    try:
        
        action = event.get('action', '').strip().lower()
        environment = event.get('environment', '').strip().lower()

        # Validate required input
        if not action or action not in ['start', 'stop']:
            raise ValueError("Missing or invalid required parameter: 'action' (start/stop)")
        
        if not environment:
            raise ValueError("Missing required parameter: 'environment' (Dev/UAT/Prod)")
        
        logger.info(f"Action received: {action}")
        logger.info(f"Environment received: {environment}")

        response = ec2_client.describe_instances(
            Filters=[
                {
                    'Name': 'tag:AutoSchedule',
                    'Values': ['True']
                },
                {
                    'Name': 'tag:Environment',
                    'Values': [environment.capitalize()] 
                }
            ]
        )

        instance_ids = []
        for reservation in response.get('Reservations', []):
            for instance in reservation.get('Instances', []):
                instance_id = instance.get('InstanceId')
                instance_ids.append(instance_id)

        logger.info(f"Matched Instances: {instance_ids}")

        # If no instances are found, then exit
        if not instance_ids: 
            logger.info("No Instances found matching the filters.") 
            return {
                "statusCode": 200,
                "body": f"No instances found to schedule in {environment}."
            }

        # Process actions
        if action == 'start':
            logger.info(f"Starting Instances: {instance_ids}...")
            ec2_client.start_instances(InstanceIds=instance_ids)
            logger.info(f"Instances - {instance_ids} started.")

        elif action == 'stop':
            logger.info(f"Stopping Instances: {instance_ids}...")
            ec2_client.stop_instances(InstanceIds=instance_ids)
            logger.info(f"Instances - {instance_ids} stopped.")

        else:
            raise ValueError(f"Unauthorized action/environment combo: {action.upper()} on {environment.upper()}")
          
        return {
            "statusCode": 200,
            "body": f"{action.upper()} executed for {len(instance_ids)} Instances in {environment.upper()} environment."
        }

    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")
        return {
            "statusCode": 500,
            "body": f"Execution failed - {str(e)}"
        }

