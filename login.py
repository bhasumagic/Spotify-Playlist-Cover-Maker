from flask import Flask, redirect, request, jsonify
import requests
import os, signal

CLIENT_ID = 'YOUR_CLIENT_ID'
CLIENT_SECRET = 'YOUR_CLIENT_SECRET'

app = Flask(__name__)

access_token = None
refresh_token = None

@app.route("/")
def index():
    return redirect(f"https://accounts.spotify.com/authorize?client_id={CLIENT_ID}&response_type=code&redirect_uri=http://localhost:5000/callback&scope=user-read-private%20user-read-email%20playlist-read-collaborative%20user-library-read%20playlist-read-private%20&state=123")

@app.route("/callback")
def callback():
    global access_token, refresh_token
    code = request.args.get("code")
    access_token, refresh_token = get_access_token(code)
    return "<center><br><br><br><br><br><br><br><br><br><br><h1>Authorization is successful!<br>You can close this tab now</h1></center>"

def get_access_token(code):
    payload = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": "http://localhost:5000/callback",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "show_dialog" : "true"
    }
    response = requests.post("https://accounts.spotify.com/api/token", data=payload)
    response_data = response.json()
    return response_data.get("access_token"), response_data.get("refresh_token")

@app.route("/data")
def get_data():
    global access_token, refresh_token
    return jsonify({
        "access_token": access_token,
        "refresh_token": refresh_token,
    })
    
@app.route('/shutdown', methods=['POST'])
def shutdown():
    os.kill(os.getpid(), signal.SIGINT)
    return 'Server shutting down...'

def main():
    app.run()