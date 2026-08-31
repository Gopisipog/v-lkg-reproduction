@echo off
echo [GCP] Setting up temporary environment on D drive to avoid space limitations on C drive...
mkdir D:\temp\gcloud_config 2>nul
set TEMP=D:\temp
set TMP=D:\temp
set CLOUDSDK_CONFIG=D:\temp\gcloud_config

echo [GCP] Please log in to your active Google Cloud Account in the browser window that opens...
call "C:\Users\gopic\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd" auth login

echo [GCP] Deploying V-LKG to Google Cloud Run...
call "C:\Users\gopic\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd" run deploy v-lkg --source . --port 8080 --allow-unauthenticated --region us-central1

pause
