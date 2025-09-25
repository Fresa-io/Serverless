def lambda_handler(event, context):
    session = event["request"]["session"]

    if len(session) > 0 and session[-1]["challengeResult"]:
        event["response"]["issueTokens"] = True
    else:
        event["response"]["challengeName"] = "CUSTOM_CHALLENGE"

    return event
