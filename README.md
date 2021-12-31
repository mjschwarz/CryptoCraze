# CryptoCraze – Blockchain and Cryptocurrency

## Description

This project implements, from scratch, a functional blockchain and cryptocurency using a 'proof of work' consensus mechanism and a SHA-256 hashing algorithm. 

The blockchain network is formed by using API's and a publish-subscribe pattern for distributing information. 

To join and interact with the blockchain network, users can access the web page and perform actions like viewing their balance, conducting transactions, and mining.

To observe a demonstration the application's functionality, check out the **Functionality** section below.

## Tools

The back end of this application is built on Python, using Flask to manage HTTP requests. The cloud service, PubNub, allows for easy integration of pub-sub into the application. Extensive testing was carried out with both the use of PyTest tests and manual testing operations to observe functionality (which have been marked with comments).

The front end was largely built using React. By utilizing React components to dynamically structure the application's interface, the amount of code needing to be written is greatly reduced. Additionally, by inverting control to React, the app's runtime efficiency is increased.

## Functionality

This gif demonstrates some of the capabilities of this application.

![App Functionality Demo](crypto_craze.gif)

## Setup and Commands

`Note: Using Python 3.10.0 and MacOS`

### Backend

**Create the Virtual Environment**
- Open a terminal
- Enter into your project directory (e.g. cd Projects)
```
python3 -m venv blockchain-env
```

**Activate the Virtual Environment:**
``` 
source blockchain-env/bin/activate
```

**Install All Packages:**
```
pip3 install -r requirements.txt
```

**Run a Module**

Make sure to activate the virtual environment.
```
python3 -m "module_path"
```
For example:
```
python3 -m backend.blockchain.block
```

**Run Test Cases**

Make sure to activate the virtual environment.
```
python3 -m pytest backend/tests
```

**Run the App and API**

Make sure to activate the virtual environment.
```
python3 -m backend.app
```

**Run a Peer Instance**

Make sure to activate the virtual environment.
```
export PEER=True && python3 -m backend.app
```

**Seed the Backend with Data**

Make sure to activate the virtual environment.
```
export SEED_DATA=True && python3 -m backend.app
```

### Frontend

**Install all Packages**

In the frontend directory:
```
npm install
```

**Run the Frontend**

In the frontend directory:
```
npm run start
```
