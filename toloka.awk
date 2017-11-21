#!/usr/bin/awk -f

BEGIN {
    print "INPUT:id", "INPUT:lemma", "INPUT:left", "INPUT:word", "INPUT:right", "GOLDEN:sense_id", "INPUT:senses";
}

NR == 1 {
    for (i=1; i<=NF; i++) ix[$i] = i;
}

NR > 1 {
    if (length(GOLD) == 0) $ix["sense_id"] = "";
    print $ix["id"], $ix["lemma"], $ix["left"], $ix["word"], $ix["right"], $ix["sense_id"], $ix["senses"];
}
