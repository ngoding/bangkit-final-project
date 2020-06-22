# bangkit-final-project
The setup method is made for unix system.

## Google Cloud Platform deployment
Make sure you have created your project on GCP and installed the cloud SDK (Google cloud integration for terminal). 
See more information here: https://cloud.google.com/sdk/

Make sure you are authenticated and set up your SDK with the project you want to deploy to.

### Deploy
```
gcloud app deploy app.yaml backend/app.yaml
```

## Local setup

### Frontend
Make sure you have yarn installed.

#### Install dependencies
```
yarn install
```

#### Compiles and hot-reloads for development
```
yarn serve
```

### Backend
Make sure you have python 3.7 and pip > 19.0 installed.

#### Create local environment
```
python3 -m venv /path/to/virtual-env
```

#### Activate local environment
```
source /path/to/virtual-env/bin/activate
```

#### Install dependencies
```
cd backend
pip install -r requirements.txt
```

#### Run the program local environment
```
python main.py
```

### Customize configuration
See [Configuration Reference](https://cli.vuejs.org/config/).
