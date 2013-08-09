TMP=/var/tmp

DATA=islands

echo Test data $DATA

FUNCTION=condense
echo Test function $FUNCTION
python bin/${FUNCTION}.py <data/${DATA}.json | python bin/${FUNCTION}_to_text.py >$TMP/${DATA}_${FUNCTION}.txt
diff $TMP/${DATA}_${FUNCTION}.txt ref/${DATA}_${FUNCTION}.txt

FUNCTION=stem
echo Test function $FUNCTION
python bin/${FUNCTION}.py <data/${DATA}.json | python bin/${FUNCTION}_to_text.py >$TMP/${DATA}_${FUNCTION}.txt
diff $TMP/${DATA}_${FUNCTION}.txt ref/${DATA}_${FUNCTION}.txt

FUNCTION=stemgraph
echo Test function $FUNCTION
python bin/${FUNCTION}.py <data/${DATA}_stem.json >$TMP/${DATA}_${FUNCTION}.txt
diff $TMP/${DATA}_${FUNCTION}.txt ref/${DATA}_${FUNCTION}.txt

echo done
