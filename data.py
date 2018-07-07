import sys, pickle, os, random
import numpy as np

punctuations = [',', '，', '。', '?', '？', '!', '！', '：', ';', '；']#断句符号
max_len = 200 #句子最大长度（字数）


def read_dict(dict_path):
    word2dictname = {}
    dictname2id = {}
    for filename in os.listdir(dict_path): 
        if len(filename) > 4 and filename[len(filename)-4:] == '.txt':
            for line in open(os.path.join(dict_path, filename)):
                line = line.strip()
                if len(line) > 0:
                    word2dictname[line] = filename[:len(filename)-4]
            if filename not in dictname2id:
                dictname2id[filename[:len(filename)-4]] = len(dictname2id)*2 + 1
    return word2dictname, dictname2id


def read_corpus(corpus_path, word2id, word2dictname, dictname2id):
    """
    read corpus and return the list of samples
    :param corpus_path:
    :return: data
    """
    data = []
    with open(corpus_path, encoding='utf-8') as fr:
        lines = fr.readlines()
    lines = punctuate_sentences(lines) #断句
    for line in lines:
        sent_ = line.strip().split(' ')
        if len(sent_) > max_len:#超长句子截断
            sent_ = sent_[:max_len]
        #print(sent_)
        if len(sent_) == 1 and len(sent_[0]) == 0:
            continue

        tag_ = get_tag(sent_, word2dictname, dictname2id)
        sent_ = sentence2id(sent_, word2id)
        #print(tag_)
        #print(sent_)

        data.append((sent_, tag_))

    return data

def punctuate_sentences(sentences):
    #断句
    res = []
    for line in sentences:
        line = line.strip()
        if len(line) == 0:
            continue
        for punc in punctuations:
            line = line.replace(' ' + punc, '\n')
        lines = line.split('\n')
        res += lines
    return res

def get_tag(sentence, word2dictname, dictname2id):
    tags = []
    for word in sentence:
        if word in word2dictname:
            dict_id = dictname2id[word2dictname[word]]
            tags += [dict_id]
            tags += [(dict_id + 1)] * (len(word) - 1)
        else:
            tags += [0] * len(word)
    return tags

def vocab_build(vocab_path, corpus_path, min_count):
    """

    :param vocab_path:
    :param corpus_path:
    :param min_count:
    :return:
    """
    data = read_corpus(corpus_path)
    word2id = {}
    for sent_, tag_ in data:
        for word in sent_:
            if word.isdigit():
                word = '<NUM>'
            elif ('\u0041' <= word <='\u005a') or ('\u0061' <= word <='\u007a'):
                word = '<ENG>'
            if word not in word2id:
                word2id[word] = [len(word2id)+1, 1]
            else:
                word2id[word][1] += 1
    low_freq_words = []
    for word, [word_id, word_freq] in word2id.items():
        if word_freq < min_count and word != '<NUM>' and word != '<ENG>':
            low_freq_words.append(word)
    for word in low_freq_words:
        del word2id[word]

    new_id = 1
    for word in word2id.keys():
        word2id[word] = new_id
        new_id += 1
    word2id['<UNK>'] = new_id
    word2id['<PAD>'] = 0

    print(len(word2id))
    with open(vocab_path, 'wb') as fw:
        pickle.dump(word2id, fw)


def sentence2id(sent, word2id):
    """

    :param sent:
    :param word2id:
    :return:
    """
    sent = sent[:max_len]
    sentence_id = []
    for word in sent:
        if word.isdigit():
            word = '<NUM>'
        elif ('\u0041' <= word <= '\u005a') or ('\u0061' <= word <= '\u007a'):
            word = '<ENG>'
        if len(word) > 1:#实体词
            sent = [word[i] for i in range(len(word))]
            #print(sent)
            ids = sentence2id(sent, word2id)
            sentence_id += ids
        elif word not in word2id:
            word = '<UNK>'
        else:
            sentence_id.append(word2id[word])
    return sentence_id


def read_dictionary(vocab_path):
    """

    :param vocab_path:
    :return:
    """
    vocab_path = os.path.join(vocab_path)
    with open(vocab_path, 'rb') as fr:
        word2id = pickle.load(fr)
    print('vocab_size:', len(word2id))
    return word2id


def random_embedding(vocab, embedding_dim):
    """

    :param vocab:
    :param embedding_dim:
    :return:
    """
    embedding_mat = np.random.uniform(-0.25, 0.25, (len(vocab), embedding_dim))
    embedding_mat = np.float32(embedding_mat)
    return embedding_mat


def pad_sequences(sequences, pad_mark=0):
    """

    :param sequences:
    :param pad_mark:
    :return:
    """
    #max_len = max(map(lambda x : len(x), sequences))
    seq_list, seq_len_list = [], []
    for seq in sequences:
        seq = list(seq)
        seq_ = seq[:max_len] + [pad_mark] * max(max_len - len(seq), 0)
        seq_list.append(seq_)
        seq_len_list.append(min(len(seq), max_len))
    return seq_list, seq_len_list


def batch_yield(data, batch_size, shuffle=False):
    """

    :param data:
    :param batch_size:
    :param vocab:
    :param tag2label:
    :param shuffle:
    :return:
    """
    if shuffle:
        random.shuffle(data)

    seqs, labels = [], []
    for (sent_, tag_) in data:
        if len(seqs) == batch_size:
            yield seqs, labels
            seqs, labels = [], []

        seqs.append(sent_)
        labels.append(tag_)

    if len(seqs) != 0:
        yield seqs, labels

