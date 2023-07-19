import random


def generate_capybara_sounds(text: str) -> str:
    n = len(text.split())+14
    dots = text.count('. ')+1
    phrases = ['фыр-фыр', 'фыр']
    something = [', ', ' — ']
    reduce = 7
    n_words = n // reduce // dots + 1

    sentence = []
    for n_sentence in range(max(1, dots-3)):
        sentence.append('Фыр')
        ln = random.randint(1, n_words)
        for word in range(random.randint(1, ln+1)):
            sentence.append(random.choice(phrases))
        sentence.append('фыр.')
    sentence = ' '.join(sentence)
    new_sentence = []
    for letter_i in range(0, len(sentence), 3):
        batch = sentence[letter_i:letter_i+3]
        if batch == 'р ф' and random.randint(0, 2) == 1:
            new_sentence.append('р'+random.choice(something)+'ф')
        else:
            new_sentence.append(batch)
    sentence = ''.join(new_sentence).replace('.Ф', '. Ф')

    sentence = ''.join(
        [random.choice(['!', '?', '...'])
         if random.randint(0, 3) == 1 and x == '.'
         else x for x in sentence])

    return sentence


def text_limit(text):
    words = text.split(' ')
    return ' '.join(words[:15])