import os


def conlleval(label_predict, label_path, metric_path):
    """

    :param label_predict:
    :param label_path:
    :param metric_path:
    :return:
    """
    eval_perl = "./conlleval_rev.pl"
    with open(label_path, "w") as fw:
        line = []
        for sent_result in label_predict:
            for char, tag, tag_ in sent_result:
                if tag == 0:
                    tag = '0'
                elif tag % 2 == 1:
                    tag = 'B-' + str(tag)
                else:
                    tag = 'I-' + str(tag)

                if tag_ == 0:
                    tag_ = '0'
                elif tag_ % 2 == 1:
                    tag_ = 'B-' + str(tag_)
                else:
                    tag_ = 'I-' + str(tag_)

                line.append("{} {} {}\n".format(char, tag, tag_))
            line.append("\n")
        fw.writelines(line)
    os.system("perl {} < {} > {}".format(eval_perl, label_path, metric_path))
    with open(metric_path) as fr:
        metrics = [line.strip() for line in fr]
    return metrics
    
