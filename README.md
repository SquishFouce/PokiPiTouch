# PokiPiTouch
PokiPiTouch<br><br>
Based upon Paulfp's Three-Factor-Authentication-Door for Raspberry Pi<br>
https://github.com/paulfp/Three-Factor-Security-Door<br><br>
Unused original code from paulfp has primarly been preserved, but some code required complete removal.<br>
All modifications to code developed in house at NEXT Labs.<br><br>
Project uses a Serial RFID reader @ 125Khz.<br>
Data is being read in ASCII and added to the database as HEX (modify the table) to avoid issues with /n and start and end characters when recieving serial transmissions. I intend to clean this up in later versions and actually pull the 12 bytes of ASCII data I need.<br>
Added Background to main screen.<br>
Disabled SMS functionality.<br>
Colorized access denied and granted messages.<br><br>
Use the detailed tutorial found at Paulfp's website for Raspberry Pi setup guide. Please note this code has been modified to instead use a Serial RFID reader instead of a USB RFID reader.<br>
https://www.switchedonnetwork.com/2017/11/10/build-the-ultimate-door-security-system-with-three-factor-authentication/
