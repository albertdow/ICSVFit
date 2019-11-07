if [ -z $2 ]
then
    echo "Must specify <script input> <script output>"
    exit
fi


INPUT=$1
OUTPUT=$2

echo "Generating job $OUTPUT"

echo "#!/bin/bash" &> $OUTPUT
echo "export X509_USER_PROXY=\$2" >> $OUTPUT
echo "voms-proxy-info -all" >> $OUTPUT
echo "voms-proxy-info -all -file \$2" >> $OUTPUT
echo "cd $PWD" >> $OUTPUT
echo "export SCRAM_ARCH=slc6_amd64_gcc630" >> $OUTPUT
echo "eval \`scramv1 runtime -sh\`" >> $OUTPUT
echo "ulimit -c 0" >> $OUTPUT
hostname >> $OUTPUT
if [ "$INPUT" == "" ]; then :
elif [[ "$INPUT" == ./* ]];
then
  echo "$INPUT" >> $OUTPUT
else
  echo "$INPUT" >> $OUTPUT
fi
chmod +x $OUTPUT
