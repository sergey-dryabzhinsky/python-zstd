#!/bin/bash

# This scripts lets you check which minimum GLIBC version an executable requires.
# Simply run './glibc-check.sh path/to/your/binary'
#
# You can set `MAX_VER` however low you want, although I (fasterthanlime)
# feel like `2.13` is a good target (For reference, Ubuntu 12.04 has GLIBC 2.15)
MAX_VER=2.34

SCRIPTPATH=$( cd $(dirname $0) ; pwd -P )
BINARY=$1

# Version comparison function in bash
vercomp () {
    if [[ $1 == $2 ]]
    then
        return 0
    fi
    local IFS=.
    local i ver1=($1) ver2=($2)
    # fill empty fields in ver1 with zeros
    for ((i=${#ver1[@]}; i<${#ver2[@]}; i++))
    do
        ver1[i]=0
    done
    for ((i=0; i<${#ver1[@]}; i++))
    do
        if [[ -z ${ver2[i]} ]]
        then
            # fill empty fields in ver2 with zeros
            ver2[i]=0
        fi
        if ((10#${ver1[i]} > 10#${ver2[i]}))
        then
            return 1
        fi
        if ((10#${ver1[i]} < 10#${ver2[i]}))
        then
            return 2
        fi
    done
    return 0
}

IFS="
"
VERS=$(objdump -T $BINARY | grep GLIBC | sed 's/.*GLIBC_\([.0-9]*\).*/\1/g' | sort -u)

for VER in $VERS; do
  vercomp $VER $MAX_VER
  COMP=$?
  if [[ $COMP -eq 1 ]]; then
    echo "Error! ${BINARY} requests GLIBC ${VER}, which is higher than target ${MAX_VER}"
    echo "Affected symbols:"
    objdump -T $BINARY | grep GLIBC_${VER}
    echo "Looking for symbols in libraries..."
    for LIBRARY in $(ldd $BINARY | cut -d ' ' -f 3); do
      echo $LIBRARY
      objdump -T $LIBRARY | fgrep GLIBC_${VER}
    done
    exit 27
  else
    echo "Found version ${VER}"
  fi
done
