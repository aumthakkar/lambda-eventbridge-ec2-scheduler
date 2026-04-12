# AWS Lambda + EventBridge EC2 Scheduler

## Description
Event-driven automation to start and stop EC2 instances using AWS Lambda, EventBridge and Boto3.

## Features
- Scheduled automation
- Cost optimisation use case
- Serverless architecture

## Architecture

### Event Scheduling Layer
- Two separate cron-based schedules are configured in EventBridge Scheduler:
  - One for starting instances with payload: `{ "action": "start" }`
  - One for stopping instances with payload: `{ "action": "stop" }`
- Each schedule emits a structured event payload (`action=start/stop`), allowing the Lambda function to dynamically determine execution behaviour
- Enables fully automated, time-based infrastructure control without manual intervention

### Compute Layer (Serverless Orchestration)
- The schedule triggers an AWS Lambda function
- AWS Lambda acts as the orchestration engine, executing logic without provisioning or managing servers

### Execution & AWS Integration (Lambda Function)
- Uses Boto3 to interact programmatically with AWS resources
- Dynamically filters EC2 instances using tags (e.g. `Environment=Dev`, `AutoSchedule=True`)
- Determines actions (start/stop) based on event context

### Resource Management Layer
- EventBridge defines *when* actions occur, while Lambda + Boto3 define *what* actions are executed on EC2 resources
- Ensures non-production resources run only when needed, reducing unnecessary compute usage

### Observability, Monitoring & Alerting
- Logs and execution metrics are captured in Amazon CloudWatch
- Enables debugging, auditing, and basic operational monitoring through logs and metrics
- A Dead-Letter Queue (DLQ) using SQS is configured on EventBridge Scheduler to capture failed event triggers
- Lambda function errors are captured using a CloudWatch Alarm, which triggers an SNS topic to send email notifications

---

## Setup / Deployment

**1. Create an IAM role for Lambda with permissions:**

     CloudWatch actions:
     - logs:CreateLogGroup
     - logs:CreateLogStream
     - logs:PutLogEvents

     EC2 permissions:
     - ec2:StartInstances
     - ec2:StopInstances
     - ec2:DescribeInstances

     Lambda invoke permission:
     - lambda:InvokeFunction
  
     SQS permission (DLQ):
     - sqs:SendMessage

**2. Deploy the Lambda function:**
   - Upload the Python code (**ec2_scheduler.py**) from this repo via AWS Console or CLI

**3. Create EventBridge Scheduler rules:**
   - Start schedule → `cron(0 8 ? * MON-FRI *)` with payload `{ "action": "start" }`
   - Stop schedule → `cron(0 18 ? * MON-FRI *)` with payload `{ "action": "stop" }`

**4. Configure target EC2 instances:**
   - Add tags:
     - AutoSchedule = True
     - Environment = Dev

**5. Create CloudWatch Alarm:**
   - Configure a `Lambda <FunctionName>:Errors` metric alarm with **Sum** statistic
   - Set threshold to `Errors >= 1`
   - Create an SNS topic with your email endpoint and link it to the alarm

---

## Example Lambda Logic

```python
action = event.get("action")

if action == "start":
    ec2.start_instances(...)
elif action == "stop":
    ec2.stop_instances(...)
```

## Use Case

This solution can be used in organisations to:
- Reduce AWS costs by shutting down non-production environments outside working hours
- Automate infrastructure operations without manual intervention
- Enforce governance via tagging strategies


## Testing

The solution was tested by:

- Manually triggering EventBridge schedules
- Verifying EC2 instance state changes
- Validating logs in CloudWatch 
- Confirming failed events are captured in SQS DLQ
- Intentionally failing the Lambda function (e.g. removing EC2 permissions) and verifying SNS email alerts for Lambda Errors