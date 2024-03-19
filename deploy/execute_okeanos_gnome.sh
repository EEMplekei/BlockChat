#!/bin/sh
# Open a terminal to each of the servers
#
# The list of servers
LIST="snf-43775 snf-43783 snf-43785 snf-43787 snf-43833"
cmdssh=$(which ssh)
total_nodes=$1
block_size=$2

#Exit if nodes is not 5 or 10
if [ "$total_nodes" != "5" ] && [ "$total_nodes" != "10" ]; then
    echo "Please provide 5 or 10 nodes"
    exit 1
fi

#Exit if block size is not 5, 10 or 20
if [ "$block_size" != "5" ] && [ "$block_size" != "10" ] && [ "$block_size" != "20" ]; then
    echo "Please provide 5, 10 or 20 as block size"
    exit 1
fi

#Change .env on remote (total_nodes and block_size) and sync_nodes
# Change .env on remote (total_nodes and block_size) and sync_nodes
echo "Changing .env on remote and syncing nodes"
ssh -t ubuntu@snf-43775.ok-kno.grnetcloud.net ./set_env.sh $total_nodes $block_size;
ssh -t ubuntu@snf-43775.ok-kno.grnetcloud.net /bin/bash -ic 'sync_nodes;' >> /dev/null 2>&1

echo "Opening terminals for the servers"
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

#Add 5 more nodes in nodes=10
if [ "$total_nodes" = "10" ]; then
    for s in $LIST
    do
        title=$(echo -n "${s}" | sed 's/^\(.\)/\U\1/')
        if [ "$s" = "$(echo $LIST | cut -d' ' -f1)" ]; then
            args="${args} --tab --title=\"$title\" --command=\"${cmdssh} -t ubuntu@${s}.ok-kno.grnetcloud.net 'sleep $sleep; python3 ~/BlockChat/backend/api.py -i eth2 -p 8002; bash'\""
        else
            args="${args} --tab --title=\"$title\" --command=\"${cmdssh} -t ubuntu@${s}.ok-kno.grnetcloud.net 'sleep $sleep; python3 ~/BlockChat/backend/api.py -i eth1 -p 8002; bash'\""
            sleep=$((sleep+1))
        fi
    done
fi

tmpfile=$(mktemp)
echo "gnome-terminal${args}" > $tmpfile
chmod 744 $tmpfile
. $tmpfile
rm $tmpfile