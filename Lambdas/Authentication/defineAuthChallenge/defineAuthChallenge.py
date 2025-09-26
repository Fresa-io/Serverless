def lambda_handler(event, context):
    try:
        # Validate event structure
        if "request" not in event:
            event["response"] = {"challengeName": "CUSTOM_CHALLENGE"}
            return event

        if "session" not in event["request"]:
            event["response"] = {"challengeName": "CUSTOM_CHALLENGE"}
            return event

        session = event["request"]["session"]

        if len(session) > 0 and session[-1]["challengeResult"]:
            event["response"]["issueTokens"] = True
        else:
            event["response"]["challengeName"] = "CUSTOM_CHALLENGE"

        return event
    except Exception as e:
        # Return error response for any unexpected issues
        event["response"] = {"challengeName": "CUSTOM_CHALLENGE"}
        return event
