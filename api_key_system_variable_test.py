import os

def get_api_key():
    api_key = os.getenv('ZHIPUAI_API_KEY')
    if not api_key:
        raise EnvironmentError("ZHIPUAI_API_KEY is not set.")
    return api_key

def main():
    api_key = get_api_key()
    print(f"ZHIPUAI_API_KEY: {api_key}")

if __name__ == "__main__":
    main()