#!/bin/bash
####################################

# -- /
#     Video file meta data information      
# -- /

# Video file local path
path=$1

# Video file name
name=$2

# Video file suffix name
suffix=$3

# Split the number of blocks
n=$4

# Split time period
dr=$5
 
# Video duration 
time=$6

# Video handle flag
vflag=$7

# Video file bitrate
br=$8

# Video stream bitrate
vb=$9

# Video code mode 
vcc=${10}

# Audio stream bitrate
ab=${11}

# Audio code mode
acc=${12}

# Audio sample rate
ar=${13}

# Audio Channels
ac=${14}

# Abs path
abspath=${15}

af="-acodec copy"
vf="-vcodec copy"
lista=""
listv=""

logfile="/tmp/handlesh.log"
####################################

# --/
#     System Commands
# --/

#FFMPEG=/usr/bin/ffmpeg
FFMPEG=/usr/local/bin/ffmpeg
FFPROBE=/usr/local/bin/ffprobe
MV=/bin/mv

####################################

IsVTCode="NO"
IsATCode="NO"

VIDEODIR=$(dirname $path)
VIDEONAME=$(basename $path)

if [ "$br" != "N/A" ]; then
   br=$(echo "$br/1000" | bc)
else
   exit 101
fi

####################################

# --/
#     Functions
# --/

function SplitAudio()
 {
   if [ "$1" == "NO" ]; then
      if [ "$ab" == "N/A" ]; then
         $FFMPEG -y -i $path -vn $vf $af  ma.mp4  >> $logfile 2>&1
      else
         $FFMPEG -y -i $path -vn $vf -ab ${ab}k -strict -2  ma.mp4  >> $logfile 2>&1
      fi
   fi
  
   if [ "$1" == "YES" ]; then
      $FFMPEG -y -i $path -vn $vf -acodec libfaac -ab ${ab}k -ar $ar -ac $ac -strict -2  ma.mp4  >> $logfile 2>&1      
   fi
 }

function SplitVideo()
 {
   if [ "$1" == "NO" ]; then
      ### - Xinglong $FFMPEG -y -i $path -an $vf -copyinkf mv.$suffix  >> $logfile 2>&1
      $FFMPEG -y -i $path -an $vf mv.$suffix  >> $logfile 2>&1
   fi

   if [ "$1" == "YES" ]; then
      ### - Xinglong $FFMPEG -y -i $path -an -vcodec h264 -vb ${vb}k  -copyinkf  mv.$suffix  >> $logfile 2>&1
      $FFMPEG -y -i $path -an -vcodec h264 -vb ${vb}k  mv.$suffix  >> $logfile 2>&1
   fi
 }
####################################

# --/
#     Handle video file of no audio stream
# --/

if [ "$vflag" == "video" ]; then
   $FFMPEG -ar 48000 -ac 2 -f s16le -i /dev/zero -i $path -shortest -c:v copy -c:a aac -strict -2 $VIDEODIR/sound.$VIDEONAME  >> $logfile 2>&1
   $MV -f $VIDEODIR/sound.$VIDEONAME $path >> $logfile 2>&1
 
   ab=2
   ar=48000
   ac=2
   acc="aac"
fi

####################################

# --/
#     Obtain audio bitrate and split audio stream from origin video file
# --/

if [ "$ab" == "N/A" ]; then
      
   if [ "$acc" == "aac" ]; then
      # Split audio stream from origin video file
      SplitAudio $IsATCode
      # Obtain audio bitrate from "ma.mp4"
      ab=$(${abspath}/parsestream.py ma.mp4 $name "ab") 
      ab=$(echo "$ab/1000" | bc)
      # Revised By Xinglong Wu on 03/21/2014
      if [ "$ab" -gt "50" ]; then ab=50; fi;
   else
      IsATCode="YES"
      #ab=$(echo "96*$ar/48000" | bc)
      # Revised By Xinglong Wu on 03/21/2014
      ab=50
      # Split audio stream from origin video file
      SplitAudio $IsATCode
   fi

else

   ab=$(echo "$ab/1000" | bc)
   # Revised By Xinglong Wu on 03/21/2014
   if [ "$ab" -gt "50" ]; then ab=50; fi;
   if [ "$acc" == "aac" ]; then
      # Split audio stream from origin video file
      SplitAudio $IsATCode
   else
      IsATCode="YES"
      # Split audio stream from origin video file
      SplitAudio $IsATCode   
   fi
   
fi


####################################

# --/
#    Obtain video bitrate and split video stream from origin video file
# --/

if [ "$vb" == "N/A" ]; then
   vb=$(echo "$br-$ab" | bc)
else
   vb=$(echo "$vb/1000" | bc)
fi

# Different video file suffix name do different processing
case $suffix in

     "m2v"|"dat"|"m2p"|"mpeg"|"m4v")
            suffix="mp4"

esac

# Different video encoding formats do different processing
case $vcc in

     "rv40")
            suffix="mp4"
            IsVTCode="YES";;

esac

# Split video stream from origin video file
SplitVideo $IsVTCode

###################################
# -- / 
#    ADD IN 20130930
#    IF VIDEO NO HAVE ANY KEY FRAME,
#    CALCULATE THE BEST SPLIT BLOCK TIME.
# -- /

function getTimeSum()
 {
    tdr=$1
    tsum=0

    for i in $(seq $n); do
       tst=`expr \( $i - 1 \) \* $tdr`
       $FFMPEG -y -i mv.$suffix -an $vf -ss $tst -t $tdr part${i}v.$suffix >> $logfile 2>&1

       pdrv=$($FFPROBE part${i}v.$suffix 2>&1 | grep "Duration" | cut -f 4 -d " " | cut -f 1 -d ",")
       vh=$(echo $pdrv | cut -f 1 -d ":")
       vm=$(echo $pdrv | cut -f 2 -d ":")
       vs=$(echo $pdrv | cut -f 3 -d ":")

       pss=$(echo "$vh*3600+$vm*60+$vs" | bc)
       tsum=$(echo "$tsum+$pss" | bc)
    done

    echo $tsum
 }

function calBestDr()
 {
	rv=10
	iv=1
	stime=$(echo "$dr-$rv" | bc)
	etime=$(echo "$dr+$rv" | bc)
	
	tdr=$stime
	tdiffold=$time
	while [ "$tdr" -le "$etime" ]; do
	      tsum=`getTimeSum $tdr`
	      tdiffnew=$(echo "$time-$tsum" | bc)
	
	      echo "dr is : $tdr , tsum is : $tsum" >> /tmp/68bbmr.log
	
	      if [ `echo "$tdiffnew*1000" | bc | awk -F. '{print $1}'` -lt `echo "$tdiffold*1000" | bc | awk -F. '{print $1}'` ]; then
	         tdiffold=$tdiffnew
	         dr=$tdr
	      fi
	
	      tdr=$(echo "$tdr+$iv" | bc)
	done
 }

####################################
# --/
#    BASE CUT FUNCTION
#    CUT THE VIDEO FILE INTO PIECES OF AUDIO AND VIDEO STREAM
#    ADJUSTMENT OFFSET TIME
# --/

function BaseSplitVideoToBlock()
  {
    i=$1
    st=$2
    drt=$3
    
    $FFMPEG -y -i mv.$suffix -an $vf -ss $st -t $drt part${i}v.$suffix >> $logfile 2>&1
    $FFMPEG -y -i ma.mp4 -vn $af -ss $st -t $drt part${i}a.mp4  >> $logfile 2>&1

    pdrv=$($FFPROBE part${i}v.$suffix 2>&1 | grep "Duration" | cut -f 4 -d " " | cut -f 1 -d ",")
    sdrv=$($FFPROBE part${i}v.$suffix 2>&1 | grep "Duration" | cut -f 6 -d " " | cut -f 1 -d ",")
    pdra=$($FFPROBE part${i}a.mp4 2>&1 | grep "Duration" | cut -f 4 -d " " | cut -f 1 -d ",")
    sdra=$($FFPROBE part${i}a.mp4 2>&1 | grep "Duration" | cut -f 6 -d " " | cut -f 1 -d ",")
    echo "PART$i RAW Duration: Video $pdrv Audio $pdra" >> /tmp/68bbmr.log
    echo "PART$i RAW Start:    Video $sdrv Audio $sdra" >> /tmp/68bbmr.log

    vh=$(echo $pdrv | cut -f 1 -d ":")
    vm=$(echo $pdrv | cut -f 2 -d ":")
    vs=$(echo $pdrv | cut -f 3 -d ":")
    ah=$(echo $pdra | cut -f 1 -d ":")
    am=$(echo $pdra | cut -f 2 -d ":")
    as=$(echo $pdra | cut -f 3 -d ":")
    
    if [ $i != 1 ]; then
       vl=$(echo "$vh*3600+$vm*60+$vs" | bc)
       al=$(echo "$ah*3600+$am*60+$as" | bc)
       echo "video length $vl" >> $logfile
       echo "aideo length $al" >> $logfile
       
       if [ `echo "$vl*100" | bc | awk -F. '{print $1}'` -lt `echo "$al*100" | bc | awk -F. '{print $1}'` ]; then
          offset=$(echo "$al - $vl" | bc)
          
          if [ `expr index $offset "."` == 1 ]; then
             offset=0$offset
          else
             offset=$offset
          fi
          
          ### - Xinglong $FFMPEG -y -i part${i}a.mp4 -ss $offset $af $vf -copyinkf tmp.mp4 >> $logfile 2>&1
          $FFMPEG -y -i part${i}a.mp4 -ss $offset $af $vf tmp.mp4 >> $logfile 2>&1
       else
          offset=$(echo "$vl - $al" | bc)
          
          if [ `expr index $offset "."` == 1 ]; then
             offset=0$offset
          else
             offset=$offset
          fi
          
          if [ $offset != 0 ]; then
             ### - Xinglong $FFMPEG -y -i part${i}a.mp4 -ss -$offset $af $vf -copyinkf tmp.mp4 >> $logfile 2>&1    
             $FFMPEG -y -i part${i}a.mp4 -ss -$offset $af $vf tmp.mp4 >> $logfile 2>&1    
          fi
       fi
       
       echo "offset for part$i $offset" >> $logfile
       mv -f tmp.mp4 part${i}a.mp4
    fi

    ### - Xinglong $FFMPEG -y -i part${i}a.mp4 -vn $af -vbsf h264_mp4toannexb -copyinkf part${i}a.megp.ts >> $logfile 2>&1
    $FFMPEG -y -i part${i}a.mp4 -vn $af -vbsf h264_mp4toannexb part${i}a.megp.ts >> $logfile 2>&1

    lista="$lista part${i}a.megp.ts"
    listv="$listv part${i}v.$suffix"


lista=`echo $lista | sed "s/ /\|/g"`

#cut video segments to avfiles directory
cp -f $listv /tmp/${name}/avfiles/

# merge the streams
### - Xinglong $FFMPEG -y -i "concat:$lista" $af -absf aac_adtstoasc -copyinkf /tmp/${name}/avfiles/ma.mp4 >> $logfile 2>&1
$FFMPEG -y -i "concat:$lista" $af -absf aac_adtstoasc /tmp/${name}/avfiles/ma.mp4 >> $logfile 2>&1
  
  }  
#########################################
# --/
#    ADD IN 20131101
# --/

function SplitVideoToBlock()
 {
    KFSplitPointArr=$1
    ArrNum=${#KFSplitPointArr[*]}
    n=$(echo "$ArrNum-1" | bc)
    
    for ((j=0;j<$n;j++))
    do 
       m=$(echo "$j+1"|bc)
       ss=${KFSplitPointArr[j]}
       t=$(echo "${KFSplitPointArr[m]}-${KFSplitPointArr[j]}" | bc)
       
       if [ `expr index $t "."` == 1 ]; then
           t=0$t
       else
           t=$t
       fi
       
       echo "Call BaseSplitVideoToBlock $m $ss $t " >> /tmp/68bbmr.log
       BaseSplitVideoToBlock $m $ss $t
    done  
 }
 
KFSplitPointStr=$(${abspath}/parsekeyframe.py $name mv.$suffix $time $dr $n)
KFSplitPointStr=$(echo $KFSplitPointStr | sed "s/|/ /g")
KFSplitPointArr=( $KFSplitPointStr )

# --/
#    Get Real PartNums 
#    Add in 20140726 
# --/
ArrNumTmp=${#KFSplitPointArr[*]}
RealPartNums=$(echo "$ArrNumTmp-1" | bc)

SplitVideoToBlock $KFSplitPointArr

#########################################
# --/
#    Detect whether a file of the last video segment contains stream
# --/

SegDuration=$($FFPROBE /tmp/${name}/avfiles/part${n}v.$suffix 2>&1 | grep "Duration" | cut -f 4 -d " " | cut -f 1 -d ",")

echo "SegDuration is : $SegDuration , file path is : /tmp/${name}/avfiles/part${n}v.$suffix" >> /tmp/68bbmr.log

if [ "$SegDuration" == "00:00:00.00" ]; then
   IsHaveStream="NO"
else
   IsHaveStream="YES"
fi

#########################################

# --/
#    Return video meta information to python script
# --/

echo "{\"suffix\":\"$suffix\",\"ab\":\"$ab\",\"vb\":\"$vb\",\"IsHaveStream\":\"$IsHaveStream\",\"RealPartNums\":\"$RealPartNums\"}"

#########################################

exit 0

