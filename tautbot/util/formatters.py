import re


# https://github.com/CloudBotIRC/CloudBot/blob/master/cloudbot/util/formatting.py
def multi_replace(text, word_dic):
    """
    Take a string and replace words that match a key in a dictionary with the associated value.
    then returns the changed text
    :rtype str
    """
    rc = re.compile('|'.join(map(re.escape, word_dic)))

    def translate(match):
        return word_dic[match.group(0)]

    return rc.sub(translate, text)
