from helper_functions import *

sentence = "Hitherto a shameful brothel man , Salim is uplifted by their meetings in his flat : ‘ My wish for an adventure with Yvette 's daughter was a wish to be taken up to the skies . ' "
keyword = "adventure"

# token_list = sentence.split()
# index = token_list.index(keyword)
# print(token_list[index])
tokenizer = get_XLMRTokenizer()
sent = "Sound carries well over water ."
encoded_dict = tokenizer.encode_plus(
                    sent,                      # Sentence to encode.
                    add_special_tokens = True, # Add '[CLS]' and '[SEP]'
                    max_length = 64,           # Pad & truncate all sentences.
                    padding='max_length',
                    return_attention_mask = True,   # Construct attn. masks.
                    return_tensors = 'pt',     # Return pytorch tensors.
            )
tokens = encoded_dict.tokens()
print(tokens)
subword_spans = [encoded_dict.token_to_chars(i) for i in range(len(tokens))]
print(subword_spans)