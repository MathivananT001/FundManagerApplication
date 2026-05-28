"""Bot Agent Lambda handlers — EventBridge-triggered reminders (US-023, US-024)."""
import json
import time
import boto3
import os

dynamodb = boto3.resource("dynamodb", region_name=os.environ.get("AWS_REGION", "ap-south-1"))
bot_log_table = dynamodb.Table(os.environ.get("DYNAMODB_BOT_ACTIVITY_LOG_TABLE", "mlm-bot-activity-log-dev"))


def _log_activity(group_id: str, activity_type: str, details: dict):
    """Write bot activity to DynamoDB."""
    bot_log_table.put_item(Item={
        "group_id": group_id,
        "timestamp": str(int(time.time() * 1000)),
        "activity_type": activity_type,
        "details": json.dumps(details),
    })


def run_payment_reminders(event, context):
    """
    EventBridge scheduled trigger — checks overdue payments and sends reminders (US-024).
    Calls Payment Service API to get unpaid members, then dispatches SMS/push via Notification Service.
    """
    import urllib.request

    payment_service_url = os.environ.get("PAYMENT_SERVICE_URL", "http://payment-service:8000")
    notification_service_url = os.environ.get("NOTIFICATION_SERVICE_URL", "http://notification-service:8000")

    # Get groups with active deadlines (simplified — in production, query RDS or an API)
    # This Lambda is triggered daily; it queries the payment service for overdue members
    try:
        req = urllib.request.Request(f"{payment_service_url}/payments/overdue")
        with urllib.request.urlopen(req) as resp:
            overdue_data = json.loads(resp.read())
    except Exception as e:
        print(f"Error fetching overdue payments: {e}")
        return {"statusCode": 500, "body": str(e)}

    for record in overdue_data.get("overdue_members", []):
        # Dispatch SMS reminder
        payload = {
            "phone_number": record["phone_number"],
            "template_key": "payment_reminder",
            "params": {"member_name": record["name"], "group_name": record["group_name"]},
            "language": record.get("language", "en"),
        }
        try:
            req = urllib.request.Request(
                f"{notification_service_url}/notifications/send-sms",
                data=json.dumps(payload).encode(),
                headers={"Content-Type": "application/json"},
            )
            urllib.request.urlopen(req)
        except Exception as e:
            print(f"Error sending reminder to {record['phone_number']}: {e}")

        _log_activity(record["group_id"], "payment_reminder", {"member_id": record["member_id"]})

    return {"statusCode": 200, "body": json.dumps({"reminders_sent": len(overdue_data.get("overdue_members", []))})}


def run_auction_reminders(event, context):
    """
    EventBridge scheduled trigger — sends auction join reminders at T-24h and T-1h (US-023).
    """
    import urllib.request

    auction_service_url = os.environ.get("AUCTION_SERVICE_URL", "http://auction-service:8000")
    notification_service_url = os.environ.get("NOTIFICATION_SERVICE_URL", "http://notification-service:8000")

    try:
        req = urllib.request.Request(f"{auction_service_url}/auctions/upcoming")
        with urllib.request.urlopen(req) as resp:
            upcoming = json.loads(resp.read())
    except Exception as e:
        print(f"Error fetching upcoming auctions: {e}")
        return {"statusCode": 500, "body": str(e)}

    for auction in upcoming.get("auctions", []):
        payload = {
            "user_ids": auction["member_user_ids"],
            "title": "Auction Reminder",
            "body": f"Auction for {auction['group_name']} starts soon!",
            "data": {"auction_id": auction["auction_id"]},
            "language": "en",
        }
        try:
            req = urllib.request.Request(
                f"{notification_service_url}/notifications/send-bulk-push",
                data=json.dumps(payload).encode(),
                headers={"Content-Type": "application/json"},
            )
            urllib.request.urlopen(req)
        except Exception as e:
            print(f"Error sending auction reminder: {e}")

        _log_activity(auction["group_id"], "auction_reminder", {"auction_id": auction["auction_id"]})

    return {"statusCode": 200, "body": json.dumps({"reminders_sent": len(upcoming.get("auctions", []))})}


def report_pre_auction_attendance(event, context):
    """
    Invoked by Auction Service — reports which non-winners are present in the WebSocket room.
    """
    auction_id = event.get("auction_id")
    group_id = event.get("group_id")

    # Query DynamoDB AuctionConnections to see who's connected
    connections_table = dynamodb.Table(
        os.environ.get("DYNAMODB_AUCTION_CONNECTIONS_TABLE", "mlm-auction-connections-dev")
    )
    response = connections_table.query(
        KeyConditionExpression="auction_id = :aid",
        ExpressionAttributeValues={":aid": auction_id},
    )
    connected_members = [item.get("member_id") for item in response.get("Items", [])]

    _log_activity(group_id, "attendance_report", {
        "auction_id": auction_id,
        "connected_count": len(connected_members),
    })

    return {
        "statusCode": 200,
        "body": json.dumps({"auction_id": auction_id, "connected_members": connected_members}),
    }
