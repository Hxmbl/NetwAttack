def load_word_list(path="src/modules/passbrute/word_list/wlist1.txt"):
    with open(path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

# usage
if __name__ == "__main__":
    words = load_word_list()
    print(words)