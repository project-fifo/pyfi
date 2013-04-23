#/usr/bin/env bash
PACKAGE="small"
DATASET="base64-1.9.1"
NET="7df94bc3-6a9f-4c88-8f80-7a8f4086b79d"

case $1 in
    setup)
        cat <<EOF | fifo vms create -p $PACKAGE -d $DATASET
{
  "alias": "riak1",
  "networks": {"net0": "$NET"},
  "metadata": {"user-script": "/opt/local/bin/sed -i.bak \\"s/pkgsrc/pkgsrc-eu-ams/\\" /opt/local/etc/pkgin/repositories.conf; /opt/local/bin/pkgin update; /opt/local/bin/pkgin -y install riak; export IP=\`ifconfig net0 | head -n 2 | tail -n 1 | awk '{print \$2}'\`; /opt/local/bin/sed -i.bak \\"s/127.0.0.1/\$IP/\\" /opt/local/etc/riak/app.config; /opt/local/bin/sed -i.bak \\"s/127.0.0.1/\$IP/\\" /opt/local/etc/riak/vm.args; svcadm enable epmd riak"}
}
EOF

        IP1=`fifo vms get riak1 | json networks[0].ip`
        echo -n 'Waiting untill riak is up and running on the primary node.'
        until curl http://${IP1}:8098 2>/dev/null >/dev/null
        do
            sleep 1
            echo -n '.'
        done
        echo " done."

        for i in 2 3 4 5
        do
            cat <<EOF | fifo vms create -p $PACKAGE -d $DATASET
  {
    "alias": "riak${i}",
    "networks": {"net0": "$NET"},
    "metadata": {"user-script": "/opt/local/bin/sed -i.bak \\"s/pkgsrc/pkgsrc-eu-ams/\\" /opt/local/etc/pkgin/repositories.conf; /opt/local/bin/pkgin update; /opt/local/bin/pkgin -y install riak; export IP=\`ifconfig net0 | head -n 2 | tail -n 1 | awk '{print \$2}'\`; /opt/local/bin/sed -i.bak \\"s/127.0.0.1/\$IP/\\" /opt/local/etc/riak/app.config; /opt/local/bin/sed -i.bak \\"s/127.0.0.1/\$IP/\\" /opt/local/etc/riak/vm.args; svcadm enable epmd riak; sleep 10; /opt/local/bin/sudo -uriak /opt/local/sbin/riak-admin cluster join riak@${IP1}; /opt/local/bin/sudo -uriak /opt/local/sbin/riak-admin cluster plan; /opt/local/bin/sudo -uriak /opt/local/sbin/riak-admin cluster commit"}
  }
EOF
            IP=`fifo vms get riak$i | json networks[0].ip`
            echo -n "Waiting untill riak is up and running on the node $i."
            until curl http://${IP}:8098 2>/dev/null >/dev/null
            do
                sleep 1
                echo -n '.'
            done
            echo " done."

        done

        for i in 1 2 3 4 5
        do
            IP=`fifo vms get riak$i | json networks[0].ip`
            echo "Node $i: $IP."
        done
        ;;
    status)
        for i in 1 2 3 4 5
        do
            IP=`fifo vms get riak$i | json networks[0].ip`
            echo -n "Node $i: $IP "
            if curl http://${IP}:8098 2>/dev/null >/dev/null
            then
                echo "up"
            else
                echo "down"
            fi
        done
        ;;
    up)
        fifo vms start riak$2
        ;;
    down)
        fifo vms stop riak$2
        ;;
    delete)
        for i in 1 2 3 4 5
        do
            fifo vms delete riak$i
        done
        ;;
    *)
        cat <<EOF
Possible commands are:
setup          - sets up the cluster
destroy        - destroys the cluster
status         - shows cluster status
up <id>        - powers up cluster node
down <id>      - shuts down cluster node
EOF
esac
