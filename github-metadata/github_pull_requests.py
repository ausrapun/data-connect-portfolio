import requests
import pandas as pd
import getpass


# connections
owner = "OWNER_NAME" 
repos = ["REPO_NAME_1", "REPO_NAME_2"]
# prompts to input github access token
access_token = getpass.getpass() #tokens can be found in settings > developer settings > personal access token


# get all pull requests (open & closed)
def get_pull_requests(owner, repo, access_token, state="all"):
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls"
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"token {access_token}"  
    }

    all_pull_requests = []
    page = 1
    per_page = 1000  # Maximum number of items per page

    while True:
        if page % 10 == 0:
            print(f"Processing batch {page}")
        params = {"page": page, "per_page": per_page, "state": state}
        response = requests.get(url, headers=headers, params=params, timeout=5)

        if response.status_code == 200:
            pull_requests = response.json()

            if not pull_requests:
                break

            all_pull_requests.extend(pull_requests)
            page += 1
        else:
            print(f"Failed to fetch pull requests. Status code: {response.status_code}")
            return None

    return all_pull_requests

all_pull_requests = []

for repo in repos:
    print(f"processing {repo}")
    pull_requests = get_pull_requests(owner, repo, access_token, state="all")
    if pull_requests:
        all_pull_requests.extend(pull_requests)


# create a dataframe
df_pull_requests = pd.DataFrame(all_pull_requests)


# sort request data fields
request_fields = df_pull_requests.apply(lambda row: {
        "repo": row["head"]["repo"]["name"],
        "pull_request_title": row["title"],
        "pull_request_number": row["number"],
        "status": row["state"],
        "author": row["user"]["login"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
        "closed_at": row["closed_at"],
        "merged_at": row["merged_at"],
        "creation_filter": row["created_at"],
        "url": row["html_url"],
        "request_url": row["url"]
    }, axis=1, result_type='expand')


# filter dates on requests. github limits 1k requests p/h per repo
request_fields['creation_filter'] = pd.to_datetime(request_fields['creation_filter'])

specified_date = pd.to_datetime('2024-01-01').tz_localize('UTC')

requests_filtered = request_fields[request_fields['creation_filter'] > specified_date]


# get pull request reviewer data
def get_reviews(owner, repo, pull_number, access_token):
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pull_number}/reviews"
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"token {access_token}" 
    }
    print(f"processing {owner=} {repo=} {pull_number=}")

    all_reviews = []
    page = 1
    per_page = 1000

    while True:
        params = {"page": page, "per_page": per_page}
        response = requests.get(url, headers=headers, params=params, timeout=5)

        if response.status_code == 200:
            reviews_data = response.json()
            if not reviews_data:
                break  # No more reviews to fetch
            all_reviews.extend(reviews_data)
            page += 1
        else:
            print(response.text)
            return None

    return all_reviews

all_reviews = []


# Fetch reviews for pull requests in each repository
for index, row in requests_filtered.iterrows():
    pull_number = row['pull_request_number']
    repo = row['repo']
    reviews_data = get_reviews(owner, repo, pull_number, access_token)
    if reviews_data:
        all_reviews.extend(reviews_data)

# Create DataFrame for all reviews
df_reviews_all = pd.DataFrame(all_reviews)


# sort review data fields
review_fields = df_reviews_all[df_reviews_all.state == 'APPROVED'] \
    .apply(lambda row: {
        "approver": row["user"]["login"],
        "approved_at": row.get("submitted_at"),
        "review_status": row["state"],
        "review_url": row["_links"]["pull_request"]["href"]
    }, axis=1, result_type='expand')


# join tables for full view
requests_reviews = pd.merge(requests_filtered, review_fields, left_on='request_url', right_on='review_url')


# output to csv locally
requests_reviews.to_csv("OUTPUT_URL.csv', index=False")