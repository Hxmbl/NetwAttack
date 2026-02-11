def test() :

    wordlist_path = input("Path (can be stored in src/modules/passbrute/word_lists/): ").strip()
    

    with open(wordlist_path, 'r', encoding="utf-8") as f:
        passwlist = [line.strip() for line in f]
        # Make this remove empty lines and spaces, also make |>> text<<| a comment in the wordlist file so that you can add comments to the wordlist file and it will ignore them.
        passwlist = [line.strip() for line in passwlist if line.strip() and not (line.startswith("|>> ") and line.endswith(" <<|"))]

if __name__ == "__main__":
    test()