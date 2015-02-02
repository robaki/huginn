FILE=$1

CLASP="/usr/local/xhail-0.5.1/clasp"
GRINGO="/usr/local/xhail-0.5.1/gringo"

java -jar /usr/local/xhail-0.5.1/xhail.jar -g $GRINGO -c $CLASP -a -f $FILE
