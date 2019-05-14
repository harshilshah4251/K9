var request = require("request");
var fs = require('fs');
//var exec = require('child_process').exec;


//repository selection dropdown
$(".multiple.selection").dropdown();



//error handling for opening json file
try {
    var json = require('./functional-areas.json').find(function(element){
        return element["category"] === "repositories";
    });
    console.log(json);
    var info = require('./functional-areas.json').find(function(element){
        return element["category"] === "information";
    });
    console.log(info);
} catch (error) {
    var json = {};
    var info = {};
}


//dictionary that will be used for translation
const dictionary = {
    "functional_area" : "Functional Areas",
    "migration" : "Migrations",
    "seeddata" : "Seeddata",
    "metadata" : "Metadata"
}


//number of files impacted(excluding duplicates and ignored files)
//const total_impacted_files = info.total-impacted-files;
//console.log(total_impacted_files);

//populate header
let headerDate = document.createElement("h5");
headerDate.innerHTML = `Start date: ${localStorage.start_date} <br /> End date: ${localStorage.end_date}`;
let headerImpactedFiles = document.createElement("h5");
let headerBranch = document.createElement("h5");
headerBranch.innerHTML = `On branch : ${localStorage.branch}`;

let divider = document.createElement("div");
divider.className = "ui section divider";
//alert(branch);

//headerImpactedFiles.innerHTML = `Total impacted files : ${total_impacted_files}`;
try{
    document.getElementById("header_information").appendChild(headerDate);
    document.getElementById("header_information").appendChild(divider.cloneNode());
    document.getElementById("header_information").appendChild(headerImpactedFiles);
    document.getElementById("header_information").appendChild(divider.cloneNode());
    document.getElementById("header_information").appendChild(headerBranch);
}catch(error){

}


//sending request on local host to get json with files mapped to functional areas
function sendRequest() {

   

    

    document.getElementById('loader').style.display = 'block';


    let start_date = document.getElementById('start_date').value;
    let end_date = document.getElementById('end_date').value;
    let start_time = document.getElementById('start_time').value;
    let end_time = document.getElementById('end_time').value;
    let branch = document.getElementById('branch').value;
    if(branch === ''){
        branch = 'master';
    }
    //alert(branch);
    setLocalStorage("start_date", start_date);
    setLocalStorage("end_date", end_date);
    setLocalStorage("branch", branch);
    let repositories_list = document.getElementById('repositories').value.split(",");
    let repositories = '[';
    for (i = 0; i < repositories_list.length; i++) {
        if (i !== repositories_list.length - 1) {
            repositories += '"' + repositories_list[i] + '", ';
        } else {
            repositories += '"' + repositories_list[i] + '"]';
        }
    }
    console.log(repositories);
    console.log(branch);
    let options = {
        method: 'POST',
        url: 'http://localhost:5000/main',
        headers:
            {
                'Content-Type': 'application/json'
            },
        formData:
            {
                start_date: start_date,
                start_time: start_time,
                end_date: end_date,
                end_time: end_time,
                repositories: repositories,
                branch: branch
            }
    };


    request(options, function (error, response, body) {
        if (error) {
            document.getElementById('loader').style.display = 'none';
            alert(body);
            throw new Error(error)
        };
        console.log(body);
        if (response.statusCode == 200) {
            fs.writeFile("functional-areas.json", body, function (err) {
                if (err) {
                    return console.log(err);
                }
                console.log("The file was saved!");
            });
            window.location.href = "repositories.html";
        } else {
            document.getElementById('loader').style.display = 'none';
            alert(body);
        }
    });


}

//validating form to check for blank values
function validateForm(form) {
    if (form === "signup") {
        if (document.getElementById("signup_email").value === "" ||
            document.getElementById("signup_password").value === "" ||
            document.getElementById("signup_client_id").value === "" ||
            document.getElementById("signup_client_secret").value === "") {
            alert("please fill out all the fields in the form");
            return false;
        } else {
            return true;
        }
    }

    else {
        return false;
    }
}

//function called everytime when program runs to check if user credentials are already present 
function verifySignedIn(){
    fs.readFile('login-credentials.json', function read(err, data) {
        if (err) {
            throw err;
        }
        content = data;
        if(content.toString() === ''){
            location.href = "signup.html";
        }else{
            refreshCredentials(JSON.parse(content));
        }
      
    });
}

//sending refresh request on localhost when credentials expire
function refreshCredentials(data){
    
    let options = {
        method: 'POST',
        url: 'http://localhost:5000/oauth',
        headers:
            {
                'Content-Type': 'application/json'
            },
        formData: data
    };

    request(options, function (error, response, body) {
        if (error) throw new Error(error);
        else{
            fs.writeFile("login-credentials.json", body, function (err) {
                if (err) {
                    return console.log(err);
                } else {
                    console.log("login credentials were refreshed!");
                    //location.href = 'index.html';
                    
                }
            });
        }
        console.log(body);
    });
}


//saving sign up credentials
function saveSignUpCredentials() {
    let validated = validateForm("signup");
    if (validated) {
        let email = document.getElementById("signup_email").value;
        let password = document.getElementById("signup_password").value;
        let client_id = document.getElementById("signup_client_id").value;
        let client_secret = document.getElementById("signup_client_secret").value;

        let credentials = {
            "email": email,
            "password": password,
            "client_id": client_id,
            "client_secret": client_secret,
            "access_token" : '',
            "refresh_token" : '',
            "expiration_time" : ''
        }
        let options = {
            method: 'POST',
            url: 'http://localhost:5000/oauth',
            headers:
                {
                    'Content-Type': 'application/json'
                },
            formData: credentials
        };
        request(options, function (error, response, body) {
            if (error) throw new Error(error);
            else if(response.statusCode == 200){
                fs.writeFile("login-credentials.json", body, function (err) {
                    if (err) {
                        return console.log(err);
                    } else {
                        console.log("login credentials were saved!");
                        //location.href = 'index.html';
                        $('.ui.modal').modal('show');
                    }
                });
            }
            else{
                alert("Bad credentials");
            }
            console.log(body);
        });        
    }
}
//Functions to create html pages


function getMigrationsTable() {
    let repository = localStorage.repository;
    console.log(repository);
    console.log("get migrations table");
    document.getElementById('impacted_area_table_div').appendChild(getTableString("Migrations", json[repository]['impacted_areas']["migration"]['files_changed']));

}

function getSeedDataTable() {
    let repository = localStorage.repository;
    console.log("get seeddata table");
    document.getElementById('impacted_area_table_div').appendChild(getTableString("SeedData", json[repository]['impacted_areas']["seeddata"]['files_changed']));
}

function getMetaDataTable(){
    let repository = localStorage.repository;
    console.log("get metadata table");
    document.getElementById('impacted_area_table_div').appendChild(getTableString("MetaData", json[repository]['impacted_areas']["metadata"]['files_changed']));   
}

function getFunctionalAreaTable() {
    console.log("get functional area table" + localStorage.functional_area);
    let functional_area_table = '';
    let functional_area = localStorage.functional_area;
    let repository = localStorage.repository;
    console.log(functional_area);
    let files_changed = json[repository]['impacted_areas']['functional_area']['areas'][functional_area]['files_changed'];
    document.getElementById('functional_area_table_div').appendChild(getTableString(functional_area, files_changed));
}

function getImpactedAreaTable() {
    let impacted_area = localStorage.impacted_area;

    switch (impacted_area) {
        case dictionary['migration']:
            getMigrationsTable();
            break;
        case dictionary['seeddata']:
            getSeedDataTable();
            break;
        case dictionary['metadata']:
            getMetaDataTable();
        break;
        case dictionary['functional_area']:
            getFunctionalAreas();
            break;

    }
}


function getTableString(title, files_changed) {
    //let title_string = '<a class="ui orange label">' + title + '</a>';
    let table = document.createElement("table");
    table.className = "ui orange small very compact table segment";
    table.style.tableLayout = "fixed";
    let table_head = document.createElement("thead");
    let table_header_row = document.createElement("tr");
    let table_body = document.createElement("tbody");    
    let headers = [
        {
            "name" : "File",
            "width" : "eight wide"
        },
        {
            "name" : "Date",
            "width" : "two wide"
        },
        {
            "name" : "Author",
            "width" : "three wide"
        },
        {
            "name" : "Commit Id",
            "width" : "one wide"
        },
        {
            "name" : "Defect",
            "width" : "two wide"
        }]
    headers.forEach(element => {
        let header = document.createElement("th");
        header.className = element["width"];
        header.innerHTML = element["name"];
        console.log(element["width"]);
        table_header_row.appendChild(header);
    });

    getRowString(files_changed).forEach(element => {
        table_body.appendChild(element);
    });
    table_head.appendChild(table_header_row);
    table.appendChild(table_head);
    table.appendChild(table_body);
    return table;
}
function getRowString(files_changed) {
    //let rows = '';
    let rows = [];
    let data = {};
    for (let i = 0; i < files_changed.length; i++) {
        let table_row = document.createElement("tr");

        data["src"] = files_changed[i]["src"];
        //data["weight"] = files_changed[i]["weight"];
        data["date"] = files_changed[i]["date"];
        //data["link"] = files_changed[i]["link"];
        data["author"] = files_changed[i]["author"];
        data["commit_id"] = files_changed[i]["commit_id"];
        data["defect_id"] = files_changed[i]["defect_id"];

        Object.keys(data).forEach(function(key){
            let table_data = document.createElement("td");
            table_data.style.wordWrap = "break-word";
            if(key === "src"){
                console.log(key);
                let link = document.createElement("a");
                link.appendChild(document.createTextNode(data[key]));
                link.href = "webpage.html";
                link.onclick = function(){
                    console.log("link clicked");
                    setLocalStorage("weblink", files_changed[i]["link"]);
                }
                table_data.appendChild(link);
            }else{
                table_data.innerHTML = data[key].join("<br>");
            }
            
            table_row.appendChild(table_data);
        });
        rows.push(table_row);
    }
    return rows;
}

//gets all functional areas and populates the html page. Uses insertion sort to sort the contents based on number of impacted files.
function getFunctionalAreas() {

    let repository = localStorage.repository;
    let functional_areas = json[repository]["impacted_areas"]["functional_area"];
    let sorted_functional_areas = [];    
    
    for(let functional_area in functional_areas['areas']){
        console.log(functional_area);
        let num_files_changed = functional_areas['areas'][functional_area]['files_changed'].length;
        if(sorted_functional_areas.length == 0){
            sorted_functional_areas.push(functional_area);
            
        }else{
            let i = 0;
            while(i < sorted_functional_areas.length && num_files_changed < functional_areas['areas'][sorted_functional_areas[i]]["files_changed"].length){
                i++;
            }
            sorted_functional_areas.splice(i, 0, functional_area);
        }
    }
    console.log(sorted_functional_areas);
    for (let functional_area in sorted_functional_areas) {
        let label_div = document.createElement("div");
        let compact_label = document.createElement("div");
        let item_div = document.createElement("a");
        //let label = document.createElement("button");
        label_div.className = 'five wide column';
        compact_label.className = "ui compact menu";
        item_div.className = "item";
        
        item_div.style.color = "white";
        compact_label.style.borderRadius = "5px";
        item_div.style.borderRadius = "5px";
        item_div.innerHTML = sorted_functional_areas[functional_area];
        let num_files_changed = functional_areas['areas'][sorted_functional_areas[functional_area]]['files_changed'].length;
        if (num_files_changed !== undefined && num_files_changed > 0) {
            let floating_div = document.createElement("div");
            //let num_files_changed = functional_areas[functional_area]['files_changed'].length;
            floating_div.className= 'floating ui yellow label';
            //converting to percentage. This percentage value means = Out of all the impacted files, x% of impacted files were mapped to this functional area.
            floating_div.innerHTML = Math.round((num_files_changed/functional_areas['total-impacted-files']) * 10000) / 100 + "%";
            item_div.style.backgroundColor = 'rgb(' + 255 + ',' + 128 + ',' + 0 + ')';
            //label.className = 'ui orange button';
            item_div.onclick = function () {
                setLocalStorage("functional_area", sorted_functional_areas[functional_area]);
                location.href = 'functional_area.html';
            }
            item_div.appendChild(floating_div);
           
            

        }else if(num_files_changed <= 0 || num_files_changed === undefined){
            //label.className = 'ui gray button';
            item_div.style.backgroundColor = 'rgb(' + 179 + ',' + 182 + ',' + 183 + ')';
        }
        //item_div.appendChild(label);
        
        compact_label.appendChild(item_div);

        label_div.appendChild(compact_label);
        //console.log(sorted_functional_areas.length);
        document.getElementById('impacted_area_table_div').appendChild(label_div);
        
    }
        
  
    
}

function getImpactedAreas() {
    let repository = localStorage.repository;
    let impacted_areas = Object.keys(json[repository]['impacted_areas']);

    for (impacted_area in impacted_areas) {
        let label = document.createElement("a");
        let label_div = document.createElement("div");
        label_div.className = 'twelve wide column';
        label.innerHTML = dictionary[impacted_areas[impacted_area]];
        //console.log(json[repository][impacted_areas[impacted_area]]["files_changed"]);
        if(impacted_areas[impacted_area] !== "functional_area" && json[repository]['impacted_areas'][impacted_areas[impacted_area]]["files_changed"].length == 0){
            label.className = 'ui gray button';
        }
        else{
            label.className = 'ui orange button';
        }
        //label.className = 'ui orange button';
        let impacted_area_name = dictionary[impacted_areas[impacted_area]];
        label.onclick = function () {
            setLocalStorage("impacted_area", impacted_area_name);
            location.href = 'impacted_area.html';
        }
        label_div.appendChild(label);
        document.getElementById('impacted_areas_labels_div').appendChild(label_div);
    }
}


function getRepositories() {
    let repositories = Object.keys(json);

   
    //console.log(repositories);
    for (let repository in repositories) {
        //console.log(repository);
        if(repositories[repository] === "category"){
            continue;
        }
        headerImpactedFiles.innerHTML += `Total impacted files ${repositories[repository]}: ${json[repositories[repository]]['total-impacted-files']}<br/>`;
        let label = document.createElement("button");
        let label_div = document.createElement("div");
        label_div.className = 'twelve wide column';
        label.innerHTML = repositories[repository];
        label.className = 'ui button';
        label.onclick = function () {
            setLocalStorage("repository", repositories[repository]);
            location.href = 'files.html';
        }
        label_div.appendChild(label);
        //figuring out impacted areas
        let areas = Object.keys(json[repositories[repository]]['impacted_areas']);
        if (areas.length == 0) {
            label.classList.add('gray');
        } else {
            label.classList.add('orange');
            for (let area in areas) {
                let symbol = document.createElement("a");
                if(json[repositories[repository]]['impacted_areas'][areas[area]]['files_changed'] == 0){
                    symbol.className = 'ui lightgrey circular label';
                    symbol.style.cursor = 'default';
                }else{
                    symbol.className = 'ui yellow circular label';
                    symbol.style.cursor = 'default';
                    
                }
                switch (areas[area]) {
                    case 'migration':
                        symbol.innerHTML = 'M';
                        label_div.appendChild(symbol);
                        break;
                    case 'metadata':
                        symbol.innerHTML = 'Me';
                        label_div.appendChild(symbol);
                        break;
                    case 'seeddata':
                        symbol.innerHTML = 'S';
                        label_div.appendChild(symbol);
                        break;
                    case 'functional_area':
                        symbol.innerHTML = 'F';
                        label_div.appendChild(symbol);
                        break;

                }
            }
        }
        document.getElementById('repositories_labels_div').appendChild(label_div);


    }
}

//saves information that needs to be transmitted between pages.
function setLocalStorage(key, value) {

    switch(key){
        case "repository":
            localStorage.repository = value;
            break;
        case "branch":
            localStorage.branch = value;
            break;
        case "functional_area":
            localStorage.functional_area = value;
            break;
        case "impacted_area":
            localStorage.impacted_area = value;
            break;
        case "weblink":
            localStorage.weblink = value;
            break;
        case "start_date":
            localStorage.start_date = value;
            break;
        case "end_date":
            localStorage.end_date = value;
            break;
    }

}

//redirect to bitbucket
function getWebView(){
    let webview = document.createElement("webview");
    const indicator = document.querySelector('.indicator')
    webview.id = "webview";
    webview.src = localStorage.weblink;
    webview.style = "display:inline-flex; width:1500px; height: 1000px;";
    webview.autosize = true;
    document.getElementById("webview_container").appendChild(webview);
    
    const loadstart = () => {
        indicator.innerText = 'loading...'
      }
  
    const loadstop = () => {
    indicator.innerText = ''
    }
    webview.addEventListener('did-start-loading', loadstart)
    webview.addEventListener('did-stop-loading', loadstop)
}








