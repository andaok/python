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

mkdir -p /tmp/$name
cd /tmp/$name 
mkdir inputfiles 
mkdir avfiles

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
      $FFMPEG -y -i $path -vn $vf $af  ma.mp4  >> $logfile 2>&1
   fi
  
   if [ "$1" == "YES" ]; then
      $FFMPEG -y -i $path -vn $vf -acodec libfaac -ab ${ab}k -ar $ar -ac $ac -strict -2  ma.mp4  >> $logfile 2>&1      
   fi
 }

function SplitVideo()
 {
   if [ "$1" == "NO" ]; then
      $FFMPEG -y -i $path -an $vf $af -copyinkf  mv.$suffix  >> $logfile 2>&1
   fi

   if [ "$1" == "YES" ]; then
      $FFMPEG -y -i $path -an -vcodec h264 -vb ${vb}k  -copyinkf  mv.$suffix  >> $logfile 2>&1
   fi
 }
####################################

# --/
#     Handle video file of no audio stream
# --/

if [ "$vflag" == "video" ]; then
   $FFMPEG -ar 48000 -ac 2 -f s16le -i /dev/zero -i $path -shortest -c:v copy -c:a aac -strict -2 $VIDEODIR/sound.$VIDEONAME  >> $logfile 2>&1
   $MV -f $VIDEODIR/sound.$VIDEONAME $path >> $logfile 2>&1
 
   ab=2000
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
   else
      IsATCode="YES"
      ab=$(echo "96*$ar/48000" | bc)
      # Split audio stream from origin video file
      SplitAudio $IsATCode
   fi

else

   ab=$(echo "$ab/1000" | bc)
   if [ "$acc" == "aac" ]; then
      # Split audio stream from origin video file
      SplitAudio $IsATCode
   else
      IsATCode="YES"

      case $ar in
           11025) if [ "$ab" -gt "64" ]; then ab=64; fi;;
           22050) if [ "$ab" -gt "128" ]; then ab=128; fi;;
           44100) if [ "$ab" -gt "256" ]; then ab=256; fi;;
           48000) if [ "$ab" -gt "278" ]; then ab=278; fi;;
      esac

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

     "m2v"|"dat"|"m2p"|"mpeg"|"m4v"|"mkv")
            suffix="mp4";;

esac

# Different video encoding formats do different processing
case $vcc in

     "rv40")
            suffix="mp4"
            IsVTCode="YES";;

esac

# Split video stream from origin video file
SplitVideo $IsVTCode

####################################
function getTimeSum()
 {
    tdr=$1
    tsum=0

    for i in $(seq $n); do
       tst=`expr \( $i - 1 \) \* $tdr`
       $FFMPEG -y -i mv.$suffix -an $vf -ss $tst -t $tdr part${i}v.$suffix -copyinkf >> $logfile 2>&1

       pdrv=$($FFPROBE part${i}v.$suffix 2>&1 | grep "Duration" | cut -f 4 -d " " | cut -f 1 -d ",")
       vh=$(echo $pdrv | cut -f 1 -d ":")
       vm=$(echo $pdrv | cut -f 2 -d ":")
       vs=$(echo $pdrv | cut -f 3 -d ":")
 
       pss=$(echo "$vh*3600+$vm*60+$vs" | bc)
       tsum=$(echo "$tsum+$pss" | bc)
    done

    echo $tsum        
 }

####################################
# --/
#    Calculate the best split block time
# --/
rv=5
iv=1
stime=$(echo "$dr-$rv" | bc)
etime=$(echo "$dr+$rv" | bc)

tdr=$stime
tdiffold=$time
while [ "$tdr" -le "$etime" ]; do
      tsum=`getTimeSum $tdr`
      tdiffnew=$(echo "$time-$tsum" | bc)

      echo "dr is : $tdr , tsum is : $tsum"
      
      if [ `echo "$tdiffnew*1000" | bc | awk -F. '{print $1}'` -lt `echo "$tdiffold*1000" | bc | awk -F. '{print $1}'` ]; then
         tdiffold=$tdiffnew
         dr=$tdr
      fi 

      tdr=$(echo "$tdr+$iv" | bc)     
done

echo "end dr is : $dr"

####################################

# --/
#    Cut the video file into pieces of audio & video streams
# --/
tsum=0
for i in $(seq $n); do
    st=`expr \( $i - 1 \) \* $dr`
    $FFMPEG -y -i mv.$suffix -an $vf -ss $st -t $dr part${i}v.$suffix -copyinkf >> $logfile 2>&1
    $FFMPEG -y -i ma.mp4 -vn $af -ss $st -t $dr part${i}a.mp4 -copyinkf >> $logfile 2>&1

    pdrv=$($FFPROBE part${i}v.$suffix 2>&1 | grep "Duration" | cut -f 4 -d " " | cut -f 1 -d ",")
    sdrv=$($FFPROBE part${i}v.$suffix 2>&1 | grep "Duration" | cut -f 6 -d " " | cut -f 1 -d ",")
    pdra=$($FFPROBE part${i}a.mp4 2>&1 | grep "Duration" | cut -f 4 -d " " | cut -f 1 -d ",")
    sdra=$($FFPROBE part${i}a.mp4 2>&1 | grep "Duration" | cut -f 6 -d " " | cut -f 1 -d ",")
    echo "PART$i RAW Duration: Video $pdrv Audio $pdra" >> $logfile
    echo "PART$i RAW Start:    Video $sdrv Audio $sdra" >> $logfile

    vh=$(echo $pdrv | cut -f 1 -d ":")
    vm=$(echo $pdrv | cut -f 2 -d ":")
    vs=$(echo $pdrv | cut -f 3 -d ":")
    ah=$(echo $pdra | cut -f 1 -d ":")
    am=$(echo $pdra | cut -f 2 -d ":")
    as=$(echo $pdra | cut -f 3 -d ":")
    
    pss=$(echo "$vh*3600+$vm*60+$vs" | bc)
    tsum=$(echo "$tsum+$pss" | bc)

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
          
          $FFMPEG -y -i part${i}a.mp4 -ss $offset $af $vf -copyinkf tmp.mp4 > $logfile 2>&1
       else
          offset=$(echo "$vl - $al" | bc)
          
          if [ `expr index $offset "."` == 1 ]; then
             offset=0$offset
          else
             offset=$offset
          fi
          
          if [ $offset != 0 ]; then
             $FFMPEG -y -i part${i}a.mp4 -ss -$offset $af $vf -copyinkf tmp.mp4 > $logfile 2>&1    
          fi
       fi
       
       echo "offset for part$i $offset" > $logfile
       cp part${i}a.mp4 part${i}a.mp4.old
       mv -f tmp.mp4 part${i}a.mp4
    fi

    $FFMPEG -y -i part${i}a.mp4 -vn $af -vbsf h264_mp4toannexb -copyinkf part${i}a.megp.ts > $logfile 2>&1

    lista="$lista part${i}a.megp.ts"
    listv="$listv part${i}v.$suffix"
done

lista=`echo $lista | sed "s/ /\|/g"`

#cut video segments to avfiles directory
cp -f $listv /tmp/${name}/avfiles/

# merge the streams
$FFMPEG -y -i "concat:$lista" $af -absf aac_adtstoasc -copyinkf /tmp/${name}/avfiles/ma.mp4 > $logfile 2>&1

#########################################
# --/
#    Detect whether a file of the last video segment contains stream
# --/

SegDuration=$($FFPROBE /tmp/${name}/avfiles/part${n}v.$suffix 2>&1 | grep "Duration" | cut -f 4 -d " " | cut -f 1 -d ",")

echo "SegDuration is : $SegDuration , file path is : /tmp/${name}/avfiles/part${n}v.$suffix" >> /tmp/videohandle.log

if [ "$SegDuration" == "00:00:00.00" ]; then
   IsHaveStream="NO"
else
   IsHaveStream="YES"
fi

#########################################

# --/
#    Return video meta information to python script
# --/

echo "{\"suffix\":\"$suffix\",\"ab\":\"$ab\",\"vb\":\"$vb\",\"IsHaveStream\":\"$IsHaveStream\"}"

echo "time sum is : $tsum, but real time is : $time"
#########################################

exit 0

