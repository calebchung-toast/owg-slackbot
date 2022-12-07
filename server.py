import os
import logging

from flask import Flask, request, make_response, Response

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_sdk.signature import SignatureVerifier

logging.basicConfig(level=logging.DEBUG)
app = Flask(__name__)
current_user_id = ""
people_waiting = []


@app.route("/slack/test", methods=["GET", "POST"])
def command():
    if request.method == "GET":
        return make_response("", 200)
    if not verifier.is_valid_request(request.get_data(), request.headers):
        return make_response("invalid request", 403)
    info = request.form

    try:
        # send user a response via DM
        im_id = slack_client.conversations_open(users=info["user_id"])["channel"]["id"]
        response = slack_client.chat_postMessage(
            channel=im_id,
            text="test123"
        )
    except SlackApiError as e:
        logging.error('Request to Slack API Failed: {}.'.format(e.response.status_code))
        logging.error(e.response)
        return make_response("", e.response.status_code)

    return make_response("", response.status_code)


@app.route("/slack/done", methods=["POST"])
def done():
    if not verifier.is_valid_request(request.get_data(), request.headers):
        return make_response("invalid request", 403)
    info = request.form

    try:
        # send user a response via DM
        user_id = info["user_id"]
        im_id = slack_client.conversations_open(users=user_id)["channel"]["id"]
        message = "Thank you! You have relinquished control over OwG Quick Test"
        global current_user_id
        if current_user_id != user_id:
            message = "Error: you do not have OwG Quick Test claimed."
        else:
            current_user_id = ""
        response = slack_client.chat_postMessage(
            channel=im_id,
            text=message
        )
    except SlackApiError as e:
        logging.error('Request to Slack API Failed: {}.'.format(e.response.status_code))
        logging.error(e.response)
        return make_response("", e.response.status_code)

    return make_response("", response.status_code)


@app.route("/slack/claim", methods=["POST"])
def claim():
    if not verifier.is_valid_request(request.get_data(), request.headers):
        return make_response("invalid request", 403)
    info = request.form

    try:
        # send user a response via DM
        user_id = info["user_id"]
        im_id = slack_client.conversations_open(users=user_id)["channel"]["id"]
        message = "You have claimed the OwG Quick Test portal. Please remember to use /done when you finish!"
        global current_user_id
        if current_user_id == user_id:
            message = "You have already claimed the OwG Quick Test portal! If you are finished, use /done."
        elif current_user_id != "":
            message = "<@" + current_user_id + "> is currently using OwG quick test. Please wait for them to finish."
            slack_client.chat_postMessage(
                channel=slack_client.conversations_open(users=current_user_id)["channel"]["id"],
                text="<@" + user_id + "> just requested to use the OwG Quick Test. Please use /done when you are finished!"
            )
        else:
            print(user_id + "has claimed the quick test portal")
            current_user_id = user_id
        response = slack_client.chat_postMessage(
            channel=im_id,
            text=message
        )
    except SlackApiError as e:
        logging.error('Request to Slack API Failed: {}.'.format(e.response.status_code))
        logging.error(e.response)
        return make_response("", e.response.status_code)

    return make_response("", response.status_code)


# Start the Flask server
if __name__ == "__main__":
    SLACK_BOT_TOKEN = os.environ['SLACK_BOT_TOKEN']
    SLACK_SIGNATURE = os.environ['SLACK_SIGNATURE']
    slack_client = WebClient(SLACK_BOT_TOKEN)
    verifier = SignatureVerifier(SLACK_SIGNATURE)

    app.run()
