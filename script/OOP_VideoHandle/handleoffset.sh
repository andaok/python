#!/bin/bash
####################################

path=$1
name=$2
suffix=$3
n=$4
dr=$5
time=$6

af="-acodec copy"
vf="-vcodec copy"
lista=""
listv=""

ffmpeg -y -i $path -an $vf $af -copyinkf  mv.$suffix  >/dev/null 2>&1
ffmpeg -y -i $path -vn $vf $af -copyinkf  ma.mp4  >/dev/null 2>&1
# cut the video file into pieces of audio & video streams
for i in $(seq $n); do
    st=`expr \( $i - 1 \) \* $dr`
    ffmpeg -y -i mv.$suffix -an $vf -ss $st -t $dr part${i}v.$suffix -copyinkf >/dev/null 2>&1
    ffmpeg -y -i ma.mp4 -vn $af -ss $st -t $dr part${i}a.mp4 -copyinkf >/dev/null 2>&1

    pdrv=$(ffprobe part${i}v.$suffix 2>&1 | grep "Duration" | cut -f 4 -d " " | cut -f 1 -d ",")
    sdrv=$(ffprobe part${i}v.$suffix 2>&1 | grep "Duration" | cut -f 6 -d " " | cut -f 1 -d ",")
    pdra=$(ffprobe part${i}a.mp4 2>&1 | grep "Duration" | cut -f 4 -d " " | cut -f 1 -d ",")
    sdra=$(ffprobe part${i}a.mp4 2>&1 | grep "Duration" | cut -f 6 -d " " | cut -f 1 -d ",")
    echo "PART$i RAW Duration: Video $pdrv Audio $pdra"
    echo "PART$i RAW Start:    Video $sdrv Audio $sdra"

    vh=$(echo $pdrv | cut -f 1 -d ":")
    vm=$(echo $pdrv | cut -f 2 -d ":")
    vs=$(echo $pdrv | cut -f 3 -d ":")
    ah=$(echo $pdra | cut -f 1 -d ":")
    am=$(echo $pdra | cut -f 2 -d ":")
    as=$(echo $pdra | cut -f 3 -d ":")
    
    if [ $i != 1 ]; then
       vl=$(echo "$vh*3600+$vm*60+$vs" | bc)
       al=$(echo "$ah*3600+$am*60+$as" | bc)
       echo "video length $vl"
       echo "aideo length $al"
       
       if [ `echo "$vl*100" | bc | awk -F. '{print $1}'` -lt `echo "$al*100" | bc | awk -F. '{print $1}'` ]; then
          offset=$(echo "$al - $vl" | bc)
          
          if [ `expr index $offset "."` == 1 ]; then
             offset=0$offset
          else
             offset=$offset
          fi
          
          ffmpeg -y -i part${i}a.mp4 -ss $offset $af $vf -copyinkf tmp.mp4 >/dev/null 2>&1
       else
          offset=$(echo "$vl - $al" | bc)
          
          if [ `expr index $offset "."` == 1 ]; then
             offset=0$offset
          else
             offset=$offset
          fi
          
          if [ $offset != 0 ]; then
             ffmpeg -y -i part${i}a.mp4 -ss -$offset $af $vf -copyinkf tmp.mp4 >/dev/null 2>&1    
          fi
       fi
       
       echo "offset for part$i $offset"
       mv -f tmp.mp4 part${i}a.mp4
    fi

    ffmpeg -y -i part${i}a.mp4 -vn $af -bsf h264_mp4toannexb -copyinkf part${i}a.megp.ts >/dev/null 2>&1

    lista="$lista part${i}a.megp.ts"
    listv="$listv part${i}v.$suffix"
done

lista=`echo $lista | sed "s/ /\|/g"`

#cut video segments to avfiles directory
cp -f $listv /tmp/${name}/avfiles/

# merge the streams
ffmpeg -y -i "concat:$lista" $af -bsf aac_adtstoasc -copyinkf /tmp/${name}/avfiles/ma.mp4 >/dev/null 2>&1



