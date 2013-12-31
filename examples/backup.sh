#!/usr/bin/env bash
fifo=../bin/fifo
vm="$2"
case $1 in
    monthly)
        $fifo vms backups $vm create monthly
        ;;
    weekly)
        last_backup=$($fifo vms backups $vm list -pH --fmt uuid,comment | grep 'monthly\|weekly' | tail -1)
        uuid=$(echo $last_backup | cut -d: -f1)
        type=$(echo $last_backup | cut -d: -f2)
        $fifo vms backups $vm create --parent $uuid -d weekly
        ;;
    daily)
        last_backup=$($fifo vms backups $vm list -pH --fmt uuid,comment | grep 'daily\|weekly' | tail -1)
        uuid=$(echo $last_backup | cut -d: -f1)
        type=$(echo $last_backup | cut -d: -f2)
        case $type in
            weekly)
                $fifo vms backups $vm create --parent $uuid daily
                ;;
            daily)
                $fifo vms backups $vm create --parent $uuid -d daily
                ;;
        esac
        ;;
esac
