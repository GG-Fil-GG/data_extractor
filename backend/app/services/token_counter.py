import tiktoken

def count_tokens(text):
    # Initialize the tokenizer for the model you are using
    tokenizer = tiktoken.get_encoding("o200k_base") 

    # Encode the text to get the tokens
    tokens = tokenizer.encode(text)

    # Return the number of tokens
    return len(tokens)
