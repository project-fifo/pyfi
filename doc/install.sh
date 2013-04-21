#!/bin/sh

MAN_PREFIX="${PREFIX}/share/man"
RONN=${RONN:-ronn}

${RONN} --version > /dev/null 2>&1

for i in *.1 *.5; do
	section=`echo ${i}|sed 's/.*\([0-9]\).*/\1/'`
	#echo ${section}
	target="${MAN_PREFIX}/man${section}"
	# check if man directory exists	
	if ! test -d ${target}; then
		mkdir -p ${target}
	fi
	echo "${i} --> ${target}"
	install -m 444 ${i} ${target}
done
