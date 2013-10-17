DATA=$1
echo Test data $DATA

FUNCTION=condense
echo Test function $FUNCTION
python "bin/${FUNCTION}.py" <"data/${DATA}/data.json" | python "bin/${FUNCTION}_to_text.py" >"$TMP/${DATA}_${FUNCTION}.txt"
diff "$TMP/${DATA}_${FUNCTION}.txt" "ref/${DATA}/${FUNCTION}.txt"

FUNCTION=boxplot
echo Test function $FUNCTION
python "bin/${FUNCTION}.py" <"data/${DATA}/data.json" >"$TMP/${DATA}_${FUNCTION}.txt"
diff "$TMP/${DATA}_${FUNCTION}.txt" "ref/${DATA}/${FUNCTION}.txt"

FUNCTION=group
echo Test function $FUNCTION
python "bin/${FUNCTION}.py" <"data/${DATA}/data.json" | python "bin/${FUNCTION}_to_text.py" >"$TMP/${DATA}_${FUNCTION}.txt"
diff "$TMP/${DATA}_${FUNCTION}.txt" "ref/${DATA}/${FUNCTION}.txt"

FUNCTION=stemgraph
echo Test function $FUNCTION
python "bin/${FUNCTION}.py" <"data/${DATA}/group.json" >"$TMP/${DATA}_${FUNCTION}.txt"
diff "$TMP/${DATA}_${FUNCTION}.txt" "ref/${DATA}/${FUNCTION}.txt"

FUNCTION=transform_zerobase
echo Test function $FUNCTION
python "bin/${FUNCTION}.py" <"data/${DATA}/data.json" >"$TMP/${DATA}_${FUNCTION}.txt"
diff "$TMP/${DATA}_${FUNCTION}.txt" "ref/${DATA}/${FUNCTION}.txt"

FUNCTION=transform_normalize
echo Test function $FUNCTION
python "bin/${FUNCTION}.py" <"data/${DATA}/data.json" >"$TMP/${DATA}_${FUNCTION}.txt"
diff "$TMP/${DATA}_${FUNCTION}.txt" "ref/${DATA}/${FUNCTION}.txt"

echo done
