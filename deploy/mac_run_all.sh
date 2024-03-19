#!/usr/bin/env bash
NODES=$1
BLOCK_SIZE=$2

if [[ $NODES -eq 5 ]]; then
    echo "NODES 5"

osascript <<EOF
tell application "Terminal"
    activate
end tell
tell application "System Events"
    keystroke "t" using command down
    set textToType to "ssh ubuntu@snf-43775.ok-kno.grnetcloud.net\n"
    keystroke textToType
    
    set textToType to "./set_env.sh 5 $BLOCK_SIZE\n"
    keystroke textToType

    set textToType to "sync_nodes\n"
    keystroke textToType

    delay 4

    set textToType to "python3 ~/BlockChat/backend/api.py -i eth2\n"
    keystroke textToType
    delay 2

end tell

delay 4

tell application "System Events"
    keystroke "t" using command down

    set textToType to "ssh ubuntu@snf-43775.ok-kno.grnetcloud.net\n"
    keystroke textToType

     -- ssh command to open a new terminal window
    set textToType to "ssh ubuntu@10.0.0.2\n"
    keystroke textToType

    set textToType to "python3 ~/BlockChat/backend/api.py -i eth1\n"
    keystroke textToType
    delay 2

end tell

delay 4

tell application "System Events"
    keystroke "t" using command down

    set textToType to "ssh ubuntu@snf-43775.ok-kno.grnetcloud.net\n"
    keystroke textToType

     -- ssh command to open a new terminal window
    set textToType to "ssh ubuntu@10.0.0.3\n"
    keystroke textToType

    set textToType to "python3 ~/BlockChat/backend/api.py -i eth1\n"
    keystroke textToType
    delay 2

end tell

delay 4

tell application "System Events"
    keystroke "t" using command down
    set textToType to "ssh ubuntu@snf-43775.ok-kno.grnetcloud.net\n"
    keystroke textToType

     -- ssh command to open a new terminal window
    set textToType to "ssh ubuntu@10.0.0.4\n"
    keystroke textToType

    set textToType to "python3 ~/BlockChat/backend/api.py -i eth1\n"
    keystroke textToType
    delay 2

end tell

delay 4

tell application "System Events"
    keystroke "t" using command down

    -- ssh command to open a new terminal window
    set textToType to "ssh ubuntu@snf-43775.ok-kno.grnetcloud.net\n"
    keystroke textToType

    -- ssh command to open a new terminal window
    set textToType to "ssh ubuntu@10.0.0.5\n"
    keystroke textToType

    set textToType to "python3 ~/BlockChat/backend/api.py -i eth1\n"
    keystroke textToType
    delay 2

end tell
EOF

elif [[ $NODES -eq 10 ]]; then
    echo "NODES 10"

osascript <<EOF
tell application "Terminal"
    activate
end tell
tell application "System Events"
    keystroke "t" using command down
    set textToType to "ssh ubuntu@snf-43775.ok-kno.grnetcloud.net\n"
    keystroke textToType
    
    set textToType to "./set_env.sh 10 $BLOCK_SIZE\n"
    keystroke textToType

    set textToType to "sync_nodes\n"
    keystroke textToType

    delay 4

    set textToType to "python3 ~/BlockChat/backend/api.py -i eth2\n"
    keystroke textToType
    delay 2

end tell

delay 4

tell application "System Events"
    keystroke "t" using command down

    set textToType to "ssh ubuntu@snf-43775.ok-kno.grnetcloud.net\n"
    keystroke textToType

     -- ssh command to open a new terminal window
    set textToType to "ssh ubuntu@10.0.0.2\n"
    keystroke textToType

    set textToType to "python3 ~/BlockChat/backend/api.py -i eth1\n"
    keystroke textToType
    delay 2

end tell

delay 4

tell application "System Events"
    keystroke "t" using command down

    set textToType to "ssh ubuntu@snf-43775.ok-kno.grnetcloud.net\n"
    keystroke textToType

     -- ssh command to open a new terminal window
    set textToType to "ssh ubuntu@10.0.0.3\n"
    keystroke textToType

    set textToType to "python3 ~/BlockChat/backend/api.py -i eth1\n"
    keystroke textToType
    delay 2

end tell

delay 4

tell application "System Events"
    keystroke "t" using command down
    set textToType to "ssh ubuntu@snf-43775.ok-kno.grnetcloud.net\n"
    keystroke textToType

     -- ssh command to open a new terminal window
    set textToType to "ssh ubuntu@10.0.0.4\n"
    keystroke textToType

    set textToType to "python3 ~/BlockChat/backend/api.py -i eth1\n"
    keystroke textToType
    delay 2

end tell

delay 4

tell application "System Events"
    keystroke "t" using command down

    -- ssh command to open a new terminal window
    set textToType to "ssh ubuntu@snf-43775.ok-kno.grnetcloud.net\n"
    keystroke textToType

    -- ssh command to open a new terminal window
    set textToType to "ssh ubuntu@10.0.0.5\n"
    keystroke textToType

    set textToType to "python3 ~/BlockChat/backend/api.py -i eth1\n"
    keystroke textToType
    delay 2

end tell
delay 4
tell application "System Events"
    keystroke "t" using command down
    set textToType to "ssh ubuntu@snf-43775.ok-kno.grnetcloud.net\n"
    keystroke textToType

    set textToType to "python3 ~/BlockChat/backend/api.py -i eth2 -p 8001\n"
    keystroke textToType
    delay 2

end tell

delay 4

tell application "System Events"
    keystroke "t" using command down

    set textToType to "ssh ubuntu@snf-43775.ok-kno.grnetcloud.net\n"
    keystroke textToType

     -- ssh command to open a new terminal window
    set textToType to "ssh ubuntu@10.0.0.2\n"
    keystroke textToType

    set textToType to "python3 ~/BlockChat/backend/api.py -i eth1 -p 8001\n"
    keystroke textToType
    delay 2

end tell

delay 4

tell application "System Events"
    keystroke "t" using command down

    set textToType to "ssh ubuntu@snf-43775.ok-kno.grnetcloud.net\n"
    keystroke textToType

     -- ssh command to open a new terminal window
    set textToType to "ssh ubuntu@10.0.0.3\n"
    keystroke textToType

    set textToType to "python3 ~/BlockChat/backend/api.py -i eth1 -p 8001\n"
    keystroke textToType
    delay 2

end tell

delay 4

tell application "System Events"
    keystroke "t" using command down
    set textToType to "ssh ubuntu@snf-43775.ok-kno.grnetcloud.net\n"
    keystroke textToType

     -- ssh command to open a new terminal window
    set textToType to "ssh ubuntu@10.0.0.4\n"
    keystroke textToType

    set textToType to "python3 ~/BlockChat/backend/api.py -i eth1 -p 8001\n"
    keystroke textToType
    delay 2

end tell

delay 4

tell application "System Events"
    keystroke "t" using command down

    -- ssh command to open a new terminal window
    set textToType to "ssh ubuntu@snf-43775.ok-kno.grnetcloud.net\n"
    keystroke textToType

    -- ssh command to open a new terminal window
    set textToType to "ssh ubuntu@10.0.0.5\n"
    keystroke textToType

    set textToType to "python3 ~/BlockChat/backend/api.py -i eth1 -p 8001\n"
    keystroke textToType
    delay 2

end tell
EOF
else
    echo "Invalid number of nodes"
    exit 1
fi
