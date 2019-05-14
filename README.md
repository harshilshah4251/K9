# Project information

* This utility tool helps in compiling a list of files that have been modified in a given time interval. The files are then mapped to a functional area based on the mapping information provided in json format. The functional areas are ranked based on severity of the changes which would help in identifying and testing specific areas before every biweekly code drops and quaterly release. 

* The project is divided into a **backend api** built in python and a **frontend** desktop application built in javascript.


# Instructions

### **Prerequisites**

* Python version >= 3.x.x
* npm >= 5.6.0

### **Setup**

#### Bitbucket setup

* Set up a consumer in bitbucket. Follow steps from this [link](https://confluence.atlassian.com/bitbucket/oauth-on-bitbucket-cloud-238027431.html)
* You only need to provide Name, check this is a private consumer, and check all the permissions listed to get the Client Id and Client Secret.
* Make sure you have your client id, client secret, bitbucket account email and password. 

#### Terminal
* Clone repository
* `cd impactedfunctionality`
* `cd ui`
* Type `./startup.txt` to install all the project dependencies

### Running the project

* `cd ui`
* Type `./run.txt` to run the application
* This will start the application. It will ask you for your email, password, client_id and client_secret the first time you run it.














