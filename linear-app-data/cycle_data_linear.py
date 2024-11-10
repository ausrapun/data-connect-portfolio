import requests
import pandas as pd
import getpass

# API key for Linear. prompts for token
token = getpass.getpass()

# Set the authorization header with the token
headers = {
    'Authorization': token
}


# linear graph ql endpoint
url = 'https://api.linear.app/graphql'


# graph ql query for cycles data in linear
# graph ql explorer for creating queries: https://studio.apollographql.com/public/Linear-API/variant/current/explorer
query = """
    query Query($cursor: String) {
      cycles(first: 50, after: $cursor) {
        pageInfo {
          endCursor
          hasNextPage
        }
        nodes {
          team {
            name
          }
          name
          id
          number
          progress
          description
          createdAt
          startsAt
          endsAt
          updatedAt
          completedAt
          scopeHistory
          inProgressScopeHistory
          completedScopeHistory
          completedIssueCountHistory
          issueCountHistory
        }
      }
    }
    """


# get this data from endpoint
all_cycles = []
cursor = None

while True:
    variables = {"cursor": cursor} if cursor else None

    response = requests.post(url=url, json={"query": query, "variables": variables}, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        cycles_data = data['data']['cycles']['nodes']
        all_cycles.extend(cycles_data)
        
        if data['data']['cycles']['pageInfo']['hasNextPage']:
            cursor = data['data']['cycles']['pageInfo']['endCursor']
        else:
            break
    else:
        print("Error:", response.text)
        break

# create a dataframe
df_cycles = pd.DataFrame(all_cycles)

# extract team names
df_cycles['team_name'] = df_cycles['team'].apply(lambda x: x.get('name'))

# Assuming 'issueCountHistory' column contains lists
# Extract the last value from each list in the 'issueCountHistory' column - how many issues in cycle
# issues in each cycle are added and remved - this account for that
df_cycles['issues_in_scope'] = df_cycles['issueCountHistory'].apply(lambda x: x[-1] if isinstance(x, list) and len(x) > 0 else None)

df_cycles['completed_issues'] = df_cycles['completedIssueCountHistory'].apply(lambda x: x[-1] if isinstance(x, list) and len(x) > 0 else None)

# rename columns
team_cycles = df_cycles.loc[:, [ 'id', 'team_name', 'number', 'progress', 'startsAt', 'endsAt','issues_in_scope','completed_issues']]

team_cycles = team_cycles.rename(columns={'number': 'cycle_number',
                                                    'team_name': 'team',
                                                    'startsAt': 'startDate',
                                                    'endsAt': 'endDate'
                                                   })


# output to csv
team_cycles.to_csv('YOUR_URL.csv', index=False)