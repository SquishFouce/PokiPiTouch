# PokiPiTouch
PokiPiTouch<br>
Based upon Paulfp's Three-Factor-Authentication-Door for Raspberry Pi<br>
https://github.com/paulfp/Three-Factor-Security-Door<br>
Unused original code from paulfp has primarly been preserved, but some code required complete removal.<br>
All modifications to code developed in house at NEXT Labs.<br>
Project uses a Serial RFID reader @ 125Khz.<br>
Data is being read in ASCII and added to the database as HEX (modify the table) to avoid issues with /n and start and end characters when recieving serial transmissions.<br>
Added Background to main screen.<br>
Colorized access denied and granted messages.<br>
