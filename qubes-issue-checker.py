from flask import Flask, request, Response
from github import Github
from pprint import pprint
import requests
import json
import os

app = Flask(__name__)

@app.route('/', methods=['POST'])
def get_webhook_response():
    payload = request.json
    event = request.headers.get("X-Github-Event")
    process_webhook_response(payload)
    
    print("New Activity on issue #: {}".format(payload["issue"]["number"]))
    # print("New Activity webhook event: {}".format(event))
    return Response(status=200)

def process_webhook_response(payload):
    issue_number    = payload["issue"]["number"]
    issue_id        = payload["issue"]["id"]
    issue_labels    = payload["issue"]["labels"]
    issue_state     = payload["issue"]["state"]
    issue_body      = payload["issue"]["body"]
    issue_comments_url = payload["issue"]["comments_url"]

    if (list(filter(lambda x: x.get('name') == 'T: bug', issue_labels))):
        get_issue_comments(issue_number, issue_comments_url)

def get_issue_comments(issue_number, issue_comments_url):
    token = os.getenv('GITHUB_TOKEN')
    comment_first_line = os.getenv('ISSUE_COMMENT_FIRST_LINE')
    headers = {'Authorization': f'token {token}', 'Accept': 'application/vnd.github.v3+json'}
    
    issue_comments = requests.get(issue_comments_url, headers=headers).json()

    # if (list(filter(lambda x: comment_first_line not in x.get('body') , issue_comments))):
    #     post_issue_comment(issue_number, issue_comments_url)

    bot_comment_exists = False
    for comment in issue_comments:
        if comment_first_line in comment["body"]:
            bot_comment_exists = True

    if not bot_comment_exists:
        post_issue_comment(issue_number, issue_comments_url)

def post_issue_comment(issue_number, issue_comments_url):
    token = os.getenv('GITHUB_TOKEN')
    comment_first_line = os.getenv('ISSUE_COMMENT_FIRST_LINE')

    data = {
        "body": comment_first_line + " Please make sure to include all the relevant log file entries in your bug report. Thank you!"
    }
    headers = {'Authorization': f'token {token}', 'Accept': 'application/vnd.github.v3+json'}
    # pprint("comment posted")
    r = requests.post(issue_comments_url, headers=headers, data=json.dumps(data))

    # g = Github(token)
    # # repo = g.get_repo("QubesOS/qubes-issues")
    # repo = g.get_repo("elric-wamugu/QubesOS-build-report")
    # issue = repo.get_issue(number=issue_number)
    # pprint(issue)
    # issue.create_issue_comment('test comment via Qubes bot!')