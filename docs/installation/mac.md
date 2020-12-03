## MAC Installation Guide

## 1. Python 3.x

* Install [Python 3.x](https://www.python.org/)

## 2. Pip3

- It should be installed with Python3

`$ python3 -m pip3 install --upgrade pip3`

## 3. Requirements

   `$ cd ~/PATH_TO/interaction-design-tool-ir`

   `$ pip3 install -r requirements.txt`

## 4. Brew

- Execute the following in a Terminal or check: [https://brew.sh](https://brew.sh)

`$ /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"`

## 5. MongoDB

The instructions below are based on: [https://docs.mongodb.com/manual/tutorial/install-mongodb-on-os-x/](https://docs.mongodb.com/manual/tutorial/install-mongodb-on-os-x/)

- Open a Terminal and do:

`$ brew tap mongodb/brew`

`$ brew install mongodb-community@4.4`

`$ brew services start mongodb-community`

- Now create a replica:

`$ vim /usr/local/etc/mongod.conf`

- Go to the section "# replication" and add the following:
   
      replication: 
        replSetName: "rs0"
   
- Restart MongoDB:

  `$ brew services restart mongodb-community`
      
- Open a mongo shell and do:

   `$ mongo`
   
   `> config = { _id: "robot-change-stream", members: [{_id: 0, host: "localhost:27017"}] };`
      
   `> rs.initiate();`
   
   `> rs.status();`


## 5. Start the tool

`$ python3 main_tool.py` ***OR*** `./scripts/design_tool.sh`

- Click "Connect" to the robot and enter the settings such as the name, realm (for the interactive robotics cloud) and/or IP (for the qi framework).


## 6. Start the robot workers

   * **Option A**: using the interactive robotics cloud (Python 3)
   
      `./scripts/mac/workers_irc.sh`
      
      ***OR***
      
      `$ python3 main_robot.py`
      
      `$ python3 main_engagement.py`
      
      ***If you get errors try: brew install openssl***
      
   * **Option B**: using qi framework (Python 2)
      
      - Install [Python 2.7](https://www.python.org/)
      
      - Download **Pepper SDK 2.5.10 - Python 2.7 SDK** from: [https://www.softbankrobotics.com/emea/en/support/pepper-naoqi-2-9/downloads-softwares](https://www.softbankrobotics.com/emea/en/support/pepper-naoqi-2-9/downloads-softwares)
      
      - Open a Terminal:
      
      `$ vim ~/.zprofile`
      
      `>> export DYLD_LIBRARY_PATH=${DYLD_LIBRARY_PATH}:/Users/PATH_TO_PYNAOQI/pynaoqi-python2.7-2.5.7.1-mac64/lib`
      
         ***Remember to set the PATH_TO_PYNAOQI to where you saved the Pepper SDK***
         
      `$ source ~/.zprofile`
   
      `$ pip2 install qi`
      
      
      - Run the tool using: 
      
      `$ ./scripts/mac/workers_qi.sh` 
      
      ***OR*** 
      
      `$ python2 main_qi_robot.py`
      
      `$ python2 main_qi_engagement.py`
      
