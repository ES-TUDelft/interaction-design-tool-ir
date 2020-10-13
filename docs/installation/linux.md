# Linux Installation guide

## 1. Python 3.x

`$ sudo apt-get install python3`

## 2 Pip3

`$ sudo apt-get install python3-pip`

## 3 Requirements

   `$ cd ~/PATH_TO/interaction-design-tool-ir`

   `$ pip3 install -r requirements.txt`

## 4 MongoDB

The instructions below are based on: [https://docs.mongodb.com/manual/tutorial/install-mongodb-on-ubuntu/](https://docs.mongodb.com/manual/tutorial/install-mongodb-on-ubuntu/)

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


## 5 Start the tool

`$ python3 main_tool.py`


## 6 Start the robot workers

   * Option A: using the interactive robotics cloud (Python 3)
      
      `$ python3 main_robot.py`
      
      `$ python3 main_engagement.py`
      
   * Option B: using qi framework (Python 2)
      
      - Download **Pepper SDK 2.5.10 - Python 2.7 SDK** from: [https://www.softbankrobotics.com/emea/en/support/pepper-naoqi-2-9/downloads-softwares](https://www.softbankrobotics.com/emea/en/support/pepper-naoqi-2-9/downloads-softwares)
      
      - Open a Terminal:
      
      `$ vim ~/.bashrc`
      
      `>> export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:/home/PATH_TO_PYNAOQI/pynaoqi-python2.7-2.5.5.5-linux64/lib`
      
         ***Remember to set the PATH_TO_PYNAOQI to where you saved the Pepper SDK***
         
      `$ source ~/.bashrc`
   
      `$ pip2 install qi`
      
      `$ python2 main_qi_robot.py`
      
