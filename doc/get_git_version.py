import re


def get_git_version_info():
    with open('../.git/gitHeadInfo.gin', 'r') as file:
        content = file.read()

    shash_match = re.search(r'shash=\{(\w+)', content)
    refnames_match = re.search(r'refnames=\{\s?\(([^)]+)\)\s?', content)

    if shash_match and refnames_match:
        shash = shash_match.group(1)
        refnames = refnames_match.group(1)
        return f"[git] Branch: {refnames}@{shash}"
    else:
        return "Version information not found"


if __name__ == "__main__":
    version_info = get_git_version_info()
    print(version_info)
