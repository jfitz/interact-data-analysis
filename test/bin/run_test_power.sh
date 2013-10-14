TMP=/var/tmp
DATA=$1
echo Test data $DATA

FUNCTION=power_group
echo Test function $FUNCTION
python bin/transform_power.py -0.5 <"data/${DATA}/data.json" >"$TMP/${DATA}_transform.txt"
python bin/transform_power.py -0.5 <"data/${DATA}/data.json"| python "bin/group.py" | python "bin/group_to_text.py" >"$TMP/${DATA}_${FUNCTION}.txt"
diff "$TMP/${DATA}_${FUNCTION}.txt" "ref/${DATA}/${FUNCTION}.txt"

FUNCTION=power_stemgraph
echo Test function $FUNCTION
python bin/transform_power.py -0.5 <"data/${DATA}/data.json" | python "bin/group.py" | python "bin/stemgraph.py" >"$TMP/${DATA}_${FUNCTION}.txt"
diff "$TMP/${DATA}_${FUNCTION}.txt" "ref/${DATA}/${FUNCTION}.txt"

echo done
