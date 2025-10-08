def lambda_handler(event, context):
    try:
        print(f"🔍 defineAuthChallenge started - Request ID: {context.aws_request_id}")
        print(f"📝 Event received: {event}")
        
        # Validate event structure
        if "request" not in event:
            print("❌ No request in event, setting CUSTOM_CHALLENGE")
            event["response"] = {"challengeName": "CUSTOM_CHALLENGE"}
            return event

        if "session" not in event["request"]:
            print("❌ No session in request, setting CUSTOM_CHALLENGE")
            event["response"] = {"challengeName": "CUSTOM_CHALLENGE"}
            return event

        session = event["request"]["session"]
        print(f"🔍 Session length: {len(session)}")

        if len(session) > 0 and session[-1]["challengeResult"]:
            print("✅ Challenge completed successfully, issuing tokens")
            event["response"]["issueTokens"] = True
        else:
            print("🔍 Challenge not completed, setting CUSTOM_CHALLENGE")
            event["response"]["challengeName"] = "CUSTOM_CHALLENGE"

        print(f"🔍 Returning response: {event['response']}")
        return event
    except Exception as e:
        print(f"❌ Error in defineAuthChallenge: {str(e)}")
        # Return error response for any unexpected issues
        event["response"] = {"challengeName": "CUSTOM_CHALLENGE"}
        return event
