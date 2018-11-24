from retriever.YouTubeRetriever import YouTubeRetriever

# install necessary python libs
# https://developers.google.com/youtube/v3/quickstart/python

# Obtaining authorization credentials: OAuth 2.0 and API keys
# https://developers.google.com/youtube/registering_an_application#Create_API_Keys

# check api traffic
# https://console.developers.google.com/apis/dashboard

# The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
# the OAuth 2.0 information for this application, including its client_id and
# client_secret.
CLIENT_SECRET_FILE = 'client_secret.json'
DEVELOPER_KEY = 'your_developer_key'
youtube_retriever = YouTubeRetriever(DEVELOPER_KEY, CLIENT_SECRET_FILE)

channel_ids = youtube_retriever.get_my_subscriptions_ids()
video_ids = youtube_retriever.get_video_ids_from_channel_ids(channel_ids[:10], verbose=True)


comments = youtube_retriever.get_comments_from_video_ids(video_ids[:10], max_comments_per_video=100, verbose=True)

# do something with comments

