# Setting up Spotify

* Go to https://developer.spotify.com/dashboard/login (create an account or login to yours)

* Click on "Create a Client ID" and fill in the required fields (e.g., RobotInteractionTool for the app name)

* Click on the app you just created and go to "Edit Settings". In the ***Redirect URIs*** field add http://localhost:8080/callback/ and click on ***SAVE*** (bottom left).

* Copy the app's the ***Client ID*** and ***Client Secret*** to the ***config.yaml*** file in "interaction_manager/properties" OR in this properties directory, create a new file named ***spotify.yaml*** and add the following:

        spotify:
            username: YOUR_USER_NAME
            client_id: YOUR_CLIENT_ID
            client_secret: YOUR_CLIENT_SECRET
            redirect_uri: http://localhost:8080/callback/
            
* The ***username*** from the previous step is your personal **Spotify** username (found in your profile: https://www.spotify.com/).

* To connect to the spotify web api ***for the first time***, you'll need a running server listening to 8080 port. You can use the server.js provided by this repository (you need to install node.js first: https://nodejs.org/en/download/) or create your own.

`$ cd ~/interaction-design-tool-ir`

`$ node es_common/server.js`

* Now, you have two options, depending on the OS:

   * **Windows** platforms: open a command prompt and do (only when connecting for the first time; otherwise use the Spotify button in the tool):
   
   `$ python interaction_manager\utils\spotify_config.py`
   
   * **Other** platforms (e.g., Linux and Mac): either do (in a terminal) *"$ python interaction_manager/utils/spotify_config.py"* or launch the interaction tool GUI and click on the "Spotify" button (in the toolbar).

* You'll be presented with a connection dialog. You can either use the default settings (that you previously put in the config.yam or spotify.yaml) or enter new ones.

* Click on the ***Connect*** button. 

        * If this is the first time you connect to Spotify (i.e., there is no cache), you will be redirected to a web browser.
        * Just *copy the URL* shown on the webpage and *paste* it in the terminal running the tool then press Enter.
        * The URL should be similar to this but longer (DO NOT USE IT, it is just an example):
            - http://localhost:8080/callback/?code=BtmyiHfVlKvGtO4mgwYJQKKOUWEeNTRm22CXrAnTRp...

* If it's successful, you'll see your playlists and tracks. Click "OK" to save the setup (if you're using the tool).

* To play a song (e.g., using the test button or the mini-player panel in the main interface), you will need an active device (i.e., a Spotify Player) that is running on either your browser or PC/Phone.

* ***NOTE:*** When the player is not able to start a song, it means the device is not active. Just refresh your Spotify Player browser or the desktop app.
