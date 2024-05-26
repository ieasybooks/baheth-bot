from dotenv import load_dotenv
import os

load_dotenv()

start_message = "start"
hadith_message = "hadith"
shamila_message = "shamila"
tafrigh_message = "tafrigh"
error_message = "error"
user_does_not_exist_message = "user does not exits"

hadith_api = os.getenv("HADITH_API")
shamela_api = os.getenv("SHAMELA_API")
tafrigh_api = os.getenv("TAFRIGH_API")
tafrigh_search_api = os.getenv("TAFRIGH_SEARCH_API")

limit = 10
users = {}

"""
users = {
    user: {
        command:,
    }
}
"""
