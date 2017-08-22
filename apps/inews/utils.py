def clean_tag(tag):
	stripped_tag = tag.strip()
	if not stripped_tag:
		return None
	return " ".join(word.lower().capitalize() for word in stripped_tag.split())
	
if __name__ == "__main__":
	print clean_tag("hello world")
	print clean_tag("   en?  ")
