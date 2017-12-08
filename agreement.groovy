#!/usr/bin/env groovy

@Grab('org.apache.commons:commons-csv:1.4')
import org.apache.commons.csv.CSVParser
import static org.apache.commons.csv.CSVFormat.TDF

@Grab('org.dkpro.statistics:dkpro-statistics-agreement:2.1.0')
import org.dkpro.statistics.agreement.coding.*
import org.dkpro.statistics.agreement.distance.NominalDistanceFunction

import java.nio.file.Paths

if (args.length != 1) {
    System.err.println('Usage: agreement.groovy file.tsv')
    System.exit(1)
}

items  = new HashMap<String, Map<String, Boolean>>()
workers = new HashMap<String, Integer>()

Paths.get(args[0]).withReader { reader ->
    CSVParser csv = new CSVParser(reader, TDF.withHeader())

    for (record in csv.iterator()) {
        if (record.get('GOLDEN:sense_id')) continue

        if (!record.get('ASSIGNMENT:status').equalsIgnoreCase('APPROVED')) continue

        taskID = record.get('INPUT:id')
        if (!items.containsKey(taskID)) items[taskID] = new HashMap<String, Boolean>()

        workerID = record.get('ASSIGNMENT:worker_id')
        items[taskID][workerID] = Integer.valueOf(record.get('OUTPUT:sense_id'))

        if (!workers.containsKey(workerID)) workers[workerID] = workers.size()
    }
}

study = new CodingAnnotationStudy(workers.size())

items.each { taskID, answers ->
    study.addItemAsArray(answers.inject(new Integer[workers.size()]) { array, workerID, answer ->
        array[workers.get(workerID)] = answer
        array
    })
}

percent = new PercentageAgreement(study)
printf('PercentageAgreement: %f\n', percent.calculateAgreement())

alphaNominal = new KrippendorffAlphaAgreement(study, new NominalDistanceFunction())
printf('KrippendorffAlphaAgreement: %f\n', alphaNominal.calculateAgreement())

randolphKappa = new RandolphKappaAgreement(study)
printf('RandolphKappaAgreement: %f\n', randolphKappa.calculateAgreement())
