# I. Linux Installation guide

## I.1. Python 3.x

`$ sudo apt-get install python3`

## I.2 Pip3

`$ sudo apt-get install python3-pip`

## I.3 Requirements

   `$ cd ~/PATH_TO/interaction-design-tool-ir`

   `$ pip3 install -r requirements.txt`

## I.4 MongoDB

The instructions below are based on: hhttps://docs.mongodb.com/manual/tutorial/install-mongodb-on-ubuntu/

- Open a Terminal and do:

`$ wget -qO - https://www.mongodb.org/static/pgp/server-4.4.asc | sudo apt-key add -`

- Create the /etc/apt/sources.list.d/mongodb-org-4.4.list file for Ubuntu 20.04 (for other versions, go the link above):

`$ echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/4.4 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-4.4.list`

`$ sudo apt-get update`

`$ sudo apt-get install -y mongodb-org`

- Check which init system is used by your platform:

`$ ps --no-headers -o comm 1`

  * Option 1) If you get: **systemd** then use the following command:
      
      `$ sudo systemctl start mongod`
      
      `$ sudo systemctl enable mongod`
      
      `$ sudo systemctl status mongod`
      
  * Option 2) If you get: **init** then do the following:
  
      `$ sudo service mongod start`
      
      `$ sudo service mongod status` 

- Now create a replica:

`$ sudo vim /etc/mongod.conf`

- Go to the section "# replication" and add the following:
   `replication: `
   `  replSetName: "rs0"`
   
- Restart MongoDB:

  * Option 1) **systemd**:
      
      `$ sudo systemctl restart mongod`
      
  * Option 2) **init**:
  
      `$ sudo service mongod restart`
      
- Open a mongo shell and do:
   `$ mongo`
   
   `> config = { _id = "robot-change-stream", members = [{_id: 0, host: "localhost:27017"}] };`
      
   `> rs.initiate();`
   
   `> rs.status();`

## I.5 Start the tool

`$ python3 main_tool.py`
