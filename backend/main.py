import requests
import json
from datetime import date
from datetime import time
from datetime import datetime, timedelta
import re
from dateutil import parser
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from flask import Flask, request
import jsonify

app = Flask(__name__)


access_token = ''
user_name = ''
password = ''
headers = ''
querystring = ''
session_requests = requests.session()
# master list of all impacted files across all commits during a time period
impacted_files_master = []
num_impacted_files_migration = 0
num_impacted_files_seeddata = 0
num_impacted_files_metadata = 0
num_impacted_files_functional_area = 0



# get access and refresh token
def get_oauth_tokens(user_name, password, client_id, client_secret):
    token_url = "https://bitbucket.org/site/oauth2/access_token"

    payload = {
        "grant_type": "password",
        "client_id": client_id,
        "client_secret": client_secret,
        "username": user_name,
        "password": password
    }
    request = Request(token_url, urlencode(payload).encode())
    data = json.loads(urlopen(request).read().decode())
    return data['access_token'], data['refresh_token'], datetime.now() + timedelta(seconds=data['expires_in'])


def refresh_token(client_id, client_secret, refresh_token):
    token_url = "https://bitbucket.org/site/oauth2/access_token"

    payload = {
        "grant_type": "refresh_token",
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token
    }
    request = Request(token_url, urlencode(payload).encode())
    data = json.loads(urlopen(request).read().decode())
    return data['access_token'], data['refresh_token'], datetime.now() + timedelta(seconds=data['expires_in'])

# perform oauth 2.0
@app.route("/oauth", methods=['POST'])
def oauth():
    global access_token
    global user_name
    global password
    global headers
    global querystring

    oauth_data = {
        "email" : request.form['email'],
        "password" : request.form['password'],
        "client_id" : request.form['client_id'],
        "client_secret" : request.form['client_secret'],
        "access_token" : request.form['access_token'],
        "refresh_token" : request.form['refresh_token'],
        "expiration_time" : request.form['expiration_time'],
    } 
    
    
    #request.form
    #print(oauth_data)
    if(not 'access_token' in oauth_data or oauth_data['access_token'] == ''):
        # TODO make request to get access token here
        oauth_data['access_token'], oauth_data['refresh_token'], oauth_data['expiration_time'] = get_oauth_tokens(
            oauth_data["email"], oauth_data['password'], oauth_data['client_id'], oauth_data['client_secret'])
        # print(oauth_data)

    elif parser.parse(oauth_data['expiration_time']).replace(tzinfo=None) < datetime.now():
        print("Refreshing access token...")
        oauth_data['access_token'], oauth_data['refresh_token'], oauth_data['expiration_time'] = refresh_token(
            oauth_data['client_id'], oauth_data['client_secret'], oauth_data['refresh_token'])
        # oauth_data['access_token'] = access_token.strip()

    access_token = oauth_data['access_token']
    user_name = oauth_data['email']
    password = oauth_data['password']
    querystring = {"access_token": access_token}
    headers = {
        'Authorization': "Bearer %s" % (access_token)
    }

    return json.dumps(oauth_data,  default=str)


#gets git style code diff in plain text format
def getCodeDiff(repository, commit_id, src):
    url = "https://api.bitbucket.org/2.0/repositories/manhattanassociates/%s/diff/%s" %(repository, commit_id[0])
    print(url)
    headers = {
    'context': "integer",
    'ignore_whitespace': "true",
    'Authorization': "Bearer %s" %(access_token)
    }
    response = requests.request("GET", url, headers=headers)
    print(response.text)
    try:
        code_diff_start = response.text.index("diff --git a/%s" %src)
        code_diff_end = response.text.index("diff --git a", code_diff_start+1)
    except ValueError:
        code_diff_end = len(response.text)
    code_diff = response.text[code_diff_start:code_diff_end]
    return code_diff

headers = {
    'context': "integer",
    'ignore_whitespace': "true",
    'Authorization': "Basic aHNoYWhAbWFuaC5jb206MjI1NFZqR1NlQ3Fy",
    'Cache-Control': "no-cache",
    'Postman-Token': "f758b0ea-ff3a-4263-9a7a-fb0c49a378ce"
    }


#adds files to functional area
def addToFunctionalArea(order_func_area_data, func_area_data, repository, link, src, weight, date, author, defect_id,  commit_id, file_changes):
    global num_impacted_files_migration
    global num_impacted_files_seeddata
    global num_impacted_files_metadata
    global num_impacted_files_functional_area

    all = next((area for area in order_func_area_data if area["name"] == "All"))
    #file_name = src[src.rfind('/')+1:len(src)]
    file_name = src
    file_name_extension = file_name.split(".")[-1]
    #code_diff= getCodeDiff(repository, commit_id, src)
    code_diff = ""
    
   
    if re.search("sql", file_name_extension):
        func_area_data[repository]['impacted_areas']['migration']['files_changed'].append(
            {
                "src": src,
                "link":link,
                "weight": weight,
                "date": date,
                "author": author,
                "commit_id": commit_id,
                "defect_id": defect_id,
                "file_changes" : file_changes,
                "code_diff" : code_diff
            }
        )
        num_impacted_files_migration += 1
        
    elif re.search("json", file_name_extension):
        func_area_data[repository]['impacted_areas']['seeddata']['files_changed'].append({"src": src,
                                                            "link":link,
                                                            "weight": weight,
                                                            "date": date,
                                                            "author": author,
                                                            "commit_id": commit_id,
                                                            "defect_id": defect_id,
                                                            "file_changes" : file_changes,
                                                            "code_diff" : code_diff})
        num_impacted_files_seeddata+=1
    elif re.search("xml", file_name_extension):
        func_area_data[repository]['impacted_areas']['metadata']['files_changed'].append({"src": src,
                                                            "link":link,
                                                            "weight": weight,
                                                            "date": date,
                                                            "author": author,
                                                            "commit_id": commit_id,
                                                            "defect_id": defect_id,
                                                            "file_changes" : file_changes,
                                                            "code_diff" : code_diff})
        num_impacted_files_metadata+=1
    #ignoring utility files.
    #checking if certain files can be mapped to all functional areas.
    elif file_name.lower() in (keyword.lower() for keyword in all["keywords"]):
        func_area_data[repository]['impacted_areas']['functional_area']['areas'].setdefault("All", {})
        func_area_data[repository]['impacted_areas']['functional_area']['areas']["All"].setdefault(
            "files_changed", [])
        func_area_data[repository]['impacted_areas']['functional_area']['areas']["All"
                                                ]["files_changed"].append(
                                                    {
                                                        "src": src,
                                                        "link":link,  
                                                        "weight": weight,
                                                        "date": date,
                                                        "author": author,
                                                        "commit_id": commit_id,
                                                        "defect_id": defect_id,
                                                        "file_changes" : file_changes,
                                                        "code_diff" : code_diff
                                                    })
        num_impacted_files_functional_area+=1


    else:
        match_found = False
        for area in order_func_area_data:
            if area == "All":
                continue
            func_area_data[repository]['impacted_areas']['functional_area']['areas'].setdefault(area['name'], {})
            func_area_data[repository]['impacted_areas']['functional_area']['areas'][area['name']].setdefault(
                "files_changed", [])
            for keyword in area["keywords"]:
                match = re.search(keyword.lower(), file_name.lower())
                if match:
                    func_area_data[repository]['impacted_areas']['functional_area']['areas'][area['name']
                                                    ]["files_changed"].append(
                                                        {
                                                            "src": src,
                                                            "link":link,  
                                                            "weight": weight,
                                                            "date": date,
                                                            "author": author,
                                                            "commit_id": commit_id,
                                                            "defect_id": defect_id,
                                                            "file_changes" : file_changes,
                                                            "code_diff" : code_diff
                                                        })

                    #print(file_name + "->" + area["name"])
                    match_found = True
        if not match_found:
            func_area_data[repository]['impacted_areas']['functional_area']['areas']['Unidentified']["files_changed"].append({
                                                              "src": src,
                                                              "link":link,
                                                              "weight": weight,
                                                              "date": date,
                                                              "author": author,
                                                              "commit_id": commit_id,
                                                              "defect_id": defect_id,
                                                              "file_changes" : file_changes,
                                                              "code_diff" : code_diff
                                                          })
            print(file_name + "->" + "Unidentified")
        num_impacted_files_functional_area+=1

    return func_area_data
    # func_area_json.seek(0)
    # json.dump(func_area_data, func_area_json, sort_keys= False, indent= 4)
    # func_area_json.truncate()


#uses bitbucket diffstat endpoint to get the impacted files.
def getImpactedFiles(session_requests, headers, link, repository, date, author, defects, commit_id):
    global impacted_files_master
    #print(commit_id)
    impacted_files_url = "https://api.bitbucket.org/2.0/repositories/manhattanassociates/%s/diffstat/%s" %(repository, commit_id)
    impacted_files_response = json.loads((session_requests.request("GET", impacted_files_url, auth=(user_name, password), headers=headers)).text)
    impacted_files = []
    for value in impacted_files_response['values']:
        # print(tag.text.strip())
        if value['status'] == "removed":
            src = value['old']['path']
        elif value['status'] == "added" or value['status'] == "modified" or value['status'] == "renamed":
            src = value['new']['path']
        
        data = {}
        if src.lower().find("test") == -1 and src.lower().find("gradle") == -1 and src.lower().find(".xsl") == -1 and src.lower().find(".md") == -1:
            impacted_files.append(src.strip())
            data['src'] = src.strip()
            #print("data['src'] " + src.strip())
            src_match_found_in_master = False
            for impacted_file in impacted_files_master:
                #print("impacted_file['src'] : " + impacted_file['src'])
                if src == impacted_file['src']:
                    impacted_file['weight'] = impacted_file['weight'] + 1
                    impacted_file['date'].append(date)
                    impacted_file['author'].append(author)
                    impacted_file['defect_id'].append(defects)
                    impacted_file['commit_id'].append(commit_id[:7])
                    impacted_file['file_changes'] = impacted_file['file_changes'] + value['lines_removed']+value['lines_added']
                    impacted_file['link'] = link
                    src_match_found_in_master = True
                    break
            if not src_match_found_in_master:
                data['weight'] = 1
                data['date'] = [date]
                data['author'] = [author]
                data['defect_id'] = [defects]
                data['commit_id'] = [commit_id[:7]]
                data['repository'] = repository
                data['file_changes'] =  value['lines_removed']+value['lines_added']
                data['link'] = link
                impacted_files_master.append(data)

    return impacted_files


def getDefects(text):
    order_defect = "[A-Z]{2,3}-\d{4,5}"
    match = re.search(order_defect, text, re.MULTILINE)
    return match


# builds the json response with author, date, and files impacted by the commit
def getCommits(url, repository, start, end):
    global headers
    global querystring
    global session_requests
    #print("token : %s\nuser_name : %s \npassword : %s" %
    #      (access_token, user_name, password))
    print(url)
    response = session_requests.request(
        "GET", url, headers=headers, params=querystring)
    print(response.status_code)
    response_json = json.loads(response.text)
    # print(response_json)

    while 'error' in response_json and re.match("Access token expired", response_json['error']['message']):
        oauth()
        response = session_requests.request(
            "GET", url, headers=headers, params=querystring)
        print(response)
        response_json = json.loads(response.text)
        # print(response.text)
        #print("token : %s\nuser_name : %s \npassword : %s" %(access_token, user_name, password))

    # structure of each repo block
    repo_block = {
        "repository": repository,
        "commits": []
    }
    last_commit_reached = False
    # regex pattern for finding defect id

    # loops through commits between start and end dates
    while True:
        for commit in response_json['values']:
            if parser.parse(commit['date']).replace(tzinfo=None) <= end and parser.parse(commit['date']).replace(tzinfo=None) >= start:
                data = {}
                data['author'] = commit['author']['raw']
                data['date'] = datetime.strftime(parser.parse(commit['date']).replace(tzinfo=None) , "%Y-%m-%d") + " " + datetime.strftime(parser.parse(commit['date']).replace(tzinfo=None) , "%H:%M:%S")
                data['commit_id'] = commit['hash'][:7]
                data['repository'] = commit['repository']['name']
                link = commit['links']['html']['href']
                match = getDefects(commit['summary']['raw'])
                if match:
                    data['defects'] = match.group()
                else:
                    data['defects'] = ''
                data['files_changed'] = getImpactedFiles(
                    session_requests, headers, link, data['repository'],data['date'], data['author'], data['defects'], commit['hash'])

                # print(data)
                repo_block['commits'].append(data)
            elif datetime.strptime(commit['date'].split('T', 1)[0], "%Y-%m-%d") < start:
                last_commit_reached = True
                break
        if not last_commit_reached and 'next' in response_json:
            url = response_json['next']
            response = session_requests.request("GET", url, headers=headers)
            response_json = json.loads(response.text)
        else:
            break

    # print(json.stringify(impacted_files_master))
    return repo_block


@app.route("/main", methods=['POST'])
def main():
    # perform authentication
    #oauth()
    global impacted_files_master
    global num_impacted_files_migration
    global num_impacted_files_seeddata
    global num_impacted_files_metadata
    global num_impacted_files_functional_area
    # resetting master list
    impacted_files_master = []
    #print(request.form)
    print(request.form['repositories'])
    print(request.form['branch'])

    start = parser.parse(
        request.form['start_date'] + " " + request.form['start_time']).replace(tzinfo=None)
    end = parser.parse(
        request.form['end_date'] + " " + request.form['end_time']).replace(tzinfo=None)

    

    print(start)
    print(end)

    
    # getting impacted files in the listed repositories
    repositories = json.loads(request.form['repositories'])
    print(repositories)
    branch = request.form['branch']
    print(branch)
    # file open mode. overwrites the file before execution and then append during execution

    blocks = []
    func_area_data = {}
    general_data = {}
    response_object = []
    general_data = {
        "category" : "information",
        "period" : datetime.strftime(start, "%Y-%m-%d") + " " + datetime.strftime(end, "%Y-%m-%d")
    }
    for repository in repositories:
        
        print(repository)
        url = "https://api.bitbucket.org/2.0/repositories/manhattanassociates/%s/commits/%s?merges=only" % (
            repository, branch)
        # get commits in the given time period along with other necessary information
        print(url)
        blocks.append(getCommits(
            url=url, repository=repository, start=start, end=end))
        
        func_area_data.setdefault(repository, {})
         # classifying as the main four categories
        func_area_data[repository].setdefault('impacted_areas', {})
        func_area_data[repository]['impacted_areas'].setdefault('migration', {})
        func_area_data[repository]['impacted_areas']['migration'].setdefault('files_changed', [])
        func_area_data[repository]['impacted_areas'].setdefault('seeddata', {})
        func_area_data[repository]['impacted_areas']['seeddata'].setdefault('files_changed', [])
        func_area_data[repository]['impacted_areas'].setdefault('metadata', {})
        func_area_data[repository]['impacted_areas']['metadata'].setdefault('files_changed', [])
        func_area_data[repository]['impacted_areas'].setdefault('functional_area', {})
        func_area_data[repository]['impacted_areas']['functional_area'].setdefault('areas', {})
        with open('maps/%s.json' %(repository)) as component_func_area_json:
            #print(func_area_data)
            component_func_area_data = json.load(component_func_area_json)
            # print(impacted_files_master.text)
            for impacted_file in impacted_files_master:
                #print(impacted_file['src'])
                func_area_data = addToFunctionalArea(
                    component_func_area_data, func_area_data, impacted_file['repository'],impacted_file['link'], impacted_file['src'], impacted_file['weight'], impacted_file['date'], impacted_file['author'], impacted_file['defect_id'], impacted_file['commit_id'], impacted_file['file_changes'])

        print("num-files-%s : %d" %(repository, len(impacted_files_master)))
        func_area_data[repository]["total-impacted-files"] = len(impacted_files_master)  
        func_area_data[repository]['impacted_areas']['migration']["total-impacted-files"] = num_impacted_files_migration
        func_area_data[repository]['impacted_areas']['seeddata']["total-impacted-files"] = num_impacted_files_seeddata
        func_area_data[repository]['impacted_areas']['metadata']["total-impacted-files"] = num_impacted_files_metadata
        func_area_data[repository]['impacted_areas']['functional_area']["total-impacted-files"] = num_impacted_files_functional_area
        print("Process completed for : " + repository)

        #resetting global vaiables
        impacted_files_master = []
        num_impacted_files_migration = 0
        num_impacted_files_seeddata = 0
        num_impacted_files_metadata = 0
        num_impacted_files_functional_area = 0

    


    func_area_data.setdefault("category", "repositories")
 

    
    
    response_object.append(general_data)
    response_object.append(func_area_data)

    with open('functional-areas.json', 'w') as func_area_json:
        json.dump(response_object, func_area_json, sort_keys=False, indent=4)


        

    # prints out the result in response.json
    # with open('response.json', 'wt') as response_json:
    #     json.dump(blocks, response_json, sort_keys=False, indent=4)

    
    return json.dumps(response_object)


# if __name__ == '__main__':
#     main()
