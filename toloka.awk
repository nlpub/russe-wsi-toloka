#!/usr/bin/awk -f

BEGIN {
    if (length(GOLD) == 0) {
        print "INPUT:id", "INPUT:lemma", "INPUT:left", "INPUT:word", "INPUT:right", "INPUT:senses";
    } else {
        print "INPUT:id", "INPUT:lemma", "INPUT:left", "INPUT:word", "INPUT:right", "GOLDEN:sense_id", "INPUT:senses";
    }
}

NR == 1 {
    for (i=1; i<=NF; i++) ix[$i] = i;
}

(NR > 1) && (length(GOLD) == 0) {
    print $ix["id"], $ix["lemma"], $ix["left"], $ix["word"], $ix["right"], $ix["senses"];
}

(NR > 1) && (length(GOLD) != 0) {
    print $ix["id"], $ix["lemma"], $ix["left"], $ix["word"], $ix["right"], $ix["sense_id"], $ix["senses"];
}
