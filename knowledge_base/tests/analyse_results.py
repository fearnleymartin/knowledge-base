

def stats():
    labels_path = 'BDD-Q-A_with_extra_criteria_no_symantec.csv'
    results_path = 'results_output.csv'

    false_positives = 0
    false_negatives = 0
    true_positives = 0
    true_negatives = 0

    with open(labels_path) as f_labels:
        with open(results_path) as f_results:
            labels = f_labels.readlines()
            results = f_results.readlines()

            for (label_, result_) in zip(labels, results):
                label = label_.split(',')[1].replace('\n','')
                if label == 'Yes':
                    label = True
                else:
                    label = False
                result = result_.split(', ')[1].replace('\n','')
                if result == 'True':
                    result = True
                else:
                    result = False
                # print(label, result)
                if label and result:
                    true_positives += 1
                elif label and not result:
                    false_negatives += 1
                elif not label and result:
                    false_positives += 1
                else:
                    true_negatives += 1

    total = true_negatives + true_positives + false_negatives + false_positives
    recall = true_positives / (true_positives + false_negatives)
    precision = true_positives / (true_positives + false_positives)
    accuracy = (true_negatives + true_positives) / total

    print('false positives: {}'.format(false_positives))
    print('false negatives: {}'.format(false_negatives))
    print('true positives: {}'.format(true_positives))
    print('true negatives: {}'.format(true_negatives))
    print('recall: {}'.format(recall))
    print('precision: {}'.format(precision))
    print('accuracy: {}'.format(accuracy))


if __name__=="__main__":
    stats()