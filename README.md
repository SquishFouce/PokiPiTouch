# PokiPiTouch
PokiPiTouch
Based upon Paulfp's Three-Factor-Authentication-Door for Raspberry Pi
https://github.com/paulfp/Three-Factor-Security-Door
Unused original code from paulfp has primarly been preserved, but some code required complete removal.
All modifications to code developed in house at NEXT Labs.
Project uses a Serial RFID reader @ 125Khz.
Data is being read in ASCII and added to the database as HEX (modify the table) to avoid issues with /n and start and end characters when recieving serial transmissions.
Added Background to main screen.
Colorized access denied and granted messages.
