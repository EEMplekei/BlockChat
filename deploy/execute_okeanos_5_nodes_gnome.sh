#!/bin/sh
# Open a terminal to each of the servers
#
# The list of servers
LIST="snf-43775 snf-43783 snf-43785 snf-43787 snf-43833"
cmdssh=$(which ssh)
sleep=1
for s in $LIST
do
    title=$(echo -n "${s}" | sed 's/^\(.\)/\U\1/')
    if [ "$s" = "$(echo $LIST | cut -d' ' -f1)" ]; then
        args="${args} --tab --title=\"$title\" --command=\"${cmdssh} -t ubuntu@${s}.ok-kno.grnetcloud.net 'python3 ~/BlockChat/backend/api.py -i eth2; bash'\""
    else
        args="${args} --tab --title=\"$title\" --command=\"${cmdssh} -t ubuntu@${s}.ok-kno.grnetcloud.net 'sleep $sleep; python3 ~/BlockChat/backend/api.py -i eth1; bash'\""
		sleep=$((sleep+1))
    fi
done

tmpfile=$(mktemp)
echo "gnome-terminal${args}" > $tmpfile
chmod 744 $tmpfile
. $tmpfile
rm $tmpfile