import logging, sys, argparse


def str2bool(v):
    # copy from StackOverflow
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


def get_entity(tag_seq, char_seq, dictname2id):
    id2dictname = {}
    for k,v in dictname2id.items():
        id2dictname[v] = k
    print('tag_seq:', tag_seq)
    print('char_seq:', char_seq)

    res = {} #{id, [word1, word2, ...]}
    i = 0
    while i < len(tag_seq):
        if tag_seq[i] % 2 == 1:
            word = char_seq[i]
            dict_id = tag_seq[i]
            i += 1
            if i < len(tag_seq) and tag_seq[i] > 0 and tag_seq[i]%2 == 0:
                while i < len(tag_seq) and tag_seq[i] > 0 and tag_seq[i]%2 == 0:
                    word += char_seq[i]
                    i += 1
            if len(word) > 1:
                if dict_id in res:
                    res[dict_id] += [word]
                else:
                    res[dict_id] = [word]
        else:
            i += 1
    str_res = ''
    for k,v in res.items():
        str_res += id2dictname[k] + ': ' + ', '.join(v) + '\n'
    return str_res.strip()

def get_logger(filename):
    logger = logging.getLogger('logger')
    logger.setLevel(logging.DEBUG)
    logging.basicConfig(format='%(message)s', level=logging.DEBUG)
    handler = logging.FileHandler(filename)
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s: %(message)s'))
    logging.getLogger().addHandler(handler)
    return logger
