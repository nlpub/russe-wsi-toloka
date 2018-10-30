#!/usr/bin/awk -f

BEGIN {
    FS = OFS = "\t";
}

NR == 1 {
    for (i=1; i <= NF; i++) ix[$i] = i
    print "id", "lemma", "sense_id", "left", "word", "right", "senses"
    next
}

{
    if (length($ix["curated_sense_id"]) > 0) {
        $ix["sense_id"] = $ix["curated_sense_id"]
    }

    print $ix["id"], $ix["lemma"], $ix["sense_id"], $ix["left"], $ix["word"], $ix["right"], $ix["senses"]
}
