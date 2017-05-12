

def stats_classification():
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
                result = result_.split(',')[1].replace('\n','')
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
    print('correctly identified: {}'.format(true_positives + true_negatives))
    print('total: {}'.format(total))


def stats_parsing():

    results_path = 'items_count.csv'

    correct_count = 0
    incorrect_count = 0
    total_posts = 0
    total_parsed_posts = 0

    with open(results_path) as f_results:
        lines = f_results.readlines()
        for line in lines:
            expected_count = int(line.split(',')[1].replace('\n', ''))
            actual_count = int(line.split(',')[2].replace('\n', ''))
            total_posts += expected_count
            total_parsed_posts += actual_count
            print(expected_count, actual_count)
            if expected_count == actual_count:
                correct_count += 1
            else:
                incorrect_count += 1

    total = correct_count + incorrect_count
    accuracy = float(correct_count) / float(total)

    print('accuracy: {}'.format(accuracy))
    print('correctly parsed pages count: {}'.format(correct_count))
    print('total pages: {}'.format(total))
    print('\n')
    print('total parsed posts: {}'.format(total_parsed_posts))
    print('total posts: {}'.format(total_posts))
    print('percentage of posts parsed: {}'.format(float(total_parsed_posts)/float(total_posts)))


if __name__ == "__main__":
    # stats_classification()
    stats_parsing()