import os
import string
import csv
from collections import Counter, defaultdict
from jiwer import compute_measures


def preprocess_lyrics(lyrics):
    translator = str.maketrans('', '', string.punctuation)
    lyrics = lyrics.translate(translator)
    lyrics = lyrics.lower()  # Convert to lowercase
    word_list = lyrics.split()
    return word_list


def shorten_transcribed_list(transcribed_list, length):
    return transcribed_list[:length]


def compute_detailed_measures(actual, transcribed):
    measures = compute_measures(actual, transcribed)

    details = {
        "deletions": Counter(),
        "substitutions": defaultdict(Counter),
        "insertions": Counter()
    }

    actual_words = actual.split()
    transcribed_words = transcribed.split()

    actual_idx = 0
    transcribed_idx = 0

    while actual_idx < len(actual_words) and transcribed_idx < len(transcribed_words):
        if actual_words[actual_idx] != transcribed_words[transcribed_idx]:
            if transcribed_idx + 1 < len(transcribed_words) and actual_words[actual_idx] == transcribed_words[
                transcribed_idx + 1]:
                details["insertions"][transcribed_words[transcribed_idx]] += 1
                transcribed_idx += 1
            elif actual_idx + 1 < len(actual_words) and actual_words[actual_idx + 1] == transcribed_words[
                transcribed_idx]:
                details["deletions"][actual_words[actual_idx]] += 1
                actual_idx += 1
            else:
                details["substitutions"][actual_words[actual_idx]][transcribed_words[transcribed_idx]] += 1
                actual_idx += 1
                transcribed_idx += 1
        else:
            actual_idx += 1
            transcribed_idx += 1

    for word in actual_words[actual_idx:]:
        details["deletions"][word] += 1
    for word in transcribed_words[transcribed_idx:]:
        details["insertions"][word] += 1

    return details, round(measures["wer"], 2)


actual_lyrics_dir = '100Hits2021_lyrics30percent/'
transcribed_lyrics_dir = 'output_transcripts/'

actual_files = os.listdir(actual_lyrics_dir)
transcribed_files = os.listdir(transcribed_lyrics_dir)

actual_files_set = set(actual_files)
transcribed_files_set = set(transcribed_files)
common_files = actual_files_set.intersection(transcribed_files_set)

overview_results = []
detailed_results = []

aggregate_deletions = Counter()
aggregate_substitutions = defaultdict(Counter)
aggregate_insertions = Counter()

for filename in common_files:
    with open(os.path.join(actual_lyrics_dir, filename), 'r') as file:
        actual_lyrics = file.read()

    with open(os.path.join(transcribed_lyrics_dir, filename), 'r') as file:
        transcribed_lyrics = file.read()

    actual_word_list = preprocess_lyrics(actual_lyrics)
    transcribed_word_list = preprocess_lyrics(transcribed_lyrics)

    transcribed_word_list = shorten_transcribed_list(transcribed_word_list, len(actual_word_list))

    details, wer_value = compute_detailed_measures(' '.join(actual_word_list), ' '.join(transcribed_word_list))

    overview_results.append({
        'file': filename,
        'tokens': len(actual_word_list),
        'WER': wer_value,
        'Deletions': sum(details["deletions"].values()),
        'Substitutions': sum(sum(subs.values()) for subs in details["substitutions"].values()),
        'Insertions': sum(details["insertions"].values())
    })

    detailed_results.append({
        'file': filename,
        'WER': wer_value,
        'Deletions': dict(details["deletions"]),
        'Substitutions': {k: dict(v) for k, v in details["substitutions"].items()},
        'Insertions': dict(details["insertions"])
    })

    aggregate_deletions.update(details["deletions"])
    for key, value in details["substitutions"].items():
        aggregate_substitutions[key].update(value)
    aggregate_insertions.update(details["insertions"])

with open('overview.csv', 'w', newline='') as csvfile:
    fieldnames = ['file', 'tokens', 'WER', 'Deletions', 'Substitutions', 'Insertions']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for result in overview_results:
        writer.writerow(result)

with open('detailed_results.csv', 'w', newline='') as csvfile:
    fieldnames = ['file', 'WER', 'Deletions', 'Substitutions', 'Insertions']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for result in detailed_results:
        writer.writerow({
            'file': result['file'],
            'WER': result['WER'],
            'Deletions': result['Deletions'],
            'Substitutions': result['Substitutions'],
            'Insertions': result['Insertions']
        })

with open('aggregate_results.csv', 'w', newline='') as csvfile:
    fieldnames = ['type', 'word', 'count', 'substituted_with']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for word, count in aggregate_deletions.items():
        writer.writerow({'type': 'deletion', 'word': word, 'count': count, 'substituted_with': ''})
    for word, substitutes in aggregate_substitutions.items():
        for sub_word, count in substitutes.items():
            writer.writerow({'type': 'substitution', 'word': word, 'count': count, 'substituted_with': sub_word})
    for word, count in aggregate_insertions.items():
        writer.writerow({'type': 'insertion', 'word': word, 'count': count, 'substituted_with': ''})

for result in detailed_results:
    print(f"File: {result['file']}")
    print(f"WER: {result['WER']}")
    print(f"Deletions: {result['Deletions']}")
    print(f"Substitutions: {result['Substitutions']}")
    print(f"Insertions: {result['Insertions']}")
    print()
