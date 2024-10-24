from assemblyai.types import TranscriptResponse


def format_time(milliseconds: int) -> str:
    seconds, milliseconds = divmod(milliseconds, 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}"


def remove_duplicates(transcription):
    sentences = transcription.split('\n')
    unique_sentences = []
    for sentence in sentences:
        if not unique_sentences or sentence != unique_sentences[-1]:
            unique_sentences.append(sentence)
    return '\n'.join(unique_sentences)


def from_text(response: TranscriptResponse, dual_channel) -> str:
    if dual_channel:
        unique_utterance_text = set()
        text = ""
        for utterance in response.utterances:
            if utterance.text not in unique_utterance_text:
                text += (f"Спикер {utterance.speaker} | {format_time(utterance.start)}, {format_time(utterance.end)}\n"
                         f"{utterance.text}\n\n")

            unique_utterance_text.add(utterance.text)
        return text
    else:
        return response.text


def simple_from_text(response: TranscriptResponse, speaker_labels) -> str:
    if speaker_labels:
        text = ""
        for utterance in response.utterances:
            text += (f"Спикер {utterance.speaker} | {format_time(utterance.start)}, {format_time(utterance.end)}\n"
                     f"{utterance.text}\n\n")
        return text
    else:
        return response.text
