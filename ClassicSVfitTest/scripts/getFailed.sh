export directory=$1
export flag=$2
export resubmit=$3

if [ $flag == 'FAILED' ]; then
  echo Failed jobs: 
elif [ $flag == 'COMPLETED' ]; then
  echo Un-completed jobs:
elif [ $flag == 'ERROR' ]; then
  echo Jobs with errors:
fi

if [[ $resubmit == 1 && "$(ls | grep "resubmit.txt" )" == "resubmit.txt" ]]; then
  rm resubmit.txt
fi

for i in $directory/*; do
  if [ $flag == 'ERROR' ]; then
    #if "$(crab status $i/ | grep Cannot find .requestcache file in CRAB project directory" != "" ]]; then
    if [[ "$(crab status $i/ | grep "Cannot find .requestcache file in CRAB project directory")" != "" ]]; then
      echo $i
    fi
  fi
  if [ $flag == 'FAILED' ]; then
    if [[ "$(crab status $i/ | grep FAILED)" != "" || "$(crab status $i/ | grep failed)" != "" ]]; then
      echo $i
      if [ $resubmit == 1 ]; then
        crab resubmit $i >> resubmit.txt
      fi
    fi
  fi
  
  if [ $flag == 'COMPLETED' ]; then
    if [[ "$(crab status $i/ | grep COMPLETED)" == "" && "$(crab status $i/ | grep completed)" == "" ]]; then
      echo $i
    fi
    
    if [ $resubmit == 1 ]; then
      if [[ "$(crab status $i/ | grep FAILED)" != "" || "$(crab status $i/ | grep failed)" != "" ]]; then
        echo Resubmitting failed jobs for: $i
        crab resubmit $i >> resubmit.txt
      fi
    fi
  fi
done
