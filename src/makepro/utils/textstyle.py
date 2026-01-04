class TextStyle:
    """Dead simple colors - c.red(), c.green(), etc."""
    
    # Basic colors
    @staticmethod
    def red(text): return f'\033[31m{text}\033[0m'
    
    @staticmethod
    def green(text): return f'\033[32m{text}\033[0m'
    
    @staticmethod
    def yellow(text): return f'\033[33m{text}\033[0m'
    
    @staticmethod
    def blue(text): return f'\033[34m{text}\033[0m'
    
    @staticmethod
    def cyan(text): return f'\033[36m{text}\033[0m'
    
    # Bold versions (b prefix)
    @staticmethod
    def bred(text): return f'\033[1;31m{text}\033[0m'
    
    @staticmethod
    def bgreen(text): return f'\033[1;32m{text}\033[0m'
    
    @staticmethod
    def byellow(text): return f'\033[1;33m{text}\033[0m'
    
    @staticmethod
    def bcyan(text): return f'\033[1;36m{text}\033[0m'
    
    # Styles
    @staticmethod
    def bold(text): return f'\033[1m{text}\033[0m'
    
    @staticmethod
    def italic(text): return f'\033[3m{text}\033[0m'
    
    @staticmethod
    def underline(text): return f'\033[4m{text}\033[0m'
    
    # Highlight specific words
    @staticmethod
    def highlight(text, word, color_func):
        return text.replace(word, color_func(word))

if __name__ == "__main__":
	# Simple colors
	print(TextStyle.red("Error message"))	
	print(TextStyle.green("Success!"))
	print(TextStyle.yellow("Warning"))

	# Highlight words in a sentence
	text = "Error: File not found"
	print(TextStyle.highlight(text, "Error", TextStyle.bred))
	print(TextStyle.highlight(text, "not found", TextStyle.yellow))

	# Multiple highlights - just chain them
	text = "Success: Installed 3 packages"
	text = TextStyle.highlight(text, "Success", TextStyle.bgreen)
	text = TextStyle.highlight(text, "3", TextStyle.cyan)
	print(text)

	# Mix colors in one line
	print(f"{TextStyle.bred('Error')}: File {TextStyle.yellow('config.txt')} not found")

	# Styles
	print(TextStyle.bold("Bold") + " and " + TextStyle.italic("italic"))
