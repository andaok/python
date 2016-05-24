#!/bin/bash

echo $($1 -show_frames -print_format csv $2 2>/dev/null | grep frame,video,1 | awk 'BEGIN { FS="," } {if ($7 != "N/A"){endsp=index($7,".")+1 ; newvalue=substr($7,1,endsp) ; if (newvalue-0.1<0){printf newvalue","} else{printf newvalue-0.1","}}}' | sed s/,$//)

