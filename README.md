# ldap-guacamole
This script will inject the yubikey-id in the Active Directory into the guacamole-db (mysql)

I'm using guacamole as 'remote-workplace' solution, so I can connect to physical machines on the local network. I freelance java-programmer
added yubikey functionality into the mysql backend. Also the guacamole-user table has been extended with the 'yubikey' field.

As the yubikey-id's (first 12 charts) are stored in (samba4) Active Directory, we need a script to add the yubikey-id into mysql database.

This script is going to take care of that. As I'm yust learning python and ldap, any help is welcome.
