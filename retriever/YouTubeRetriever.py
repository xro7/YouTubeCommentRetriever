from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account and requires requests to use an SSL connection.
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'


class YouTubeRetriever:

    def __init__(self, dev_key, client_secret_path):
        self.dev_key = dev_key
        self.client_secret = client_secret_path
        self.api_service_name = API_SERVICE_NAME
        self.api_version = API_VERSION
        self.OAuth_connection = self.get_authenticated_service()
        self.API_connection = self.connect_to_api()

    # Connection for API requests
    def connect_to_api(self):
        return build(self.api_service_name, self.api_version, developerKey=self.dev_key)

    # OAuth 2.0 Authentication
    def get_authenticated_service(self):
        flow = InstalledAppFlow.from_client_secrets_file(self.client_secret, SCOPES)
        credentials = flow.run_console()
        return build(self.api_service_name, self.api_version, credentials=credentials)

    def get_my_subscriptions_ids(self):
        # https://developers.google.com/youtube/v3/docs/subscriptions/list
        print('Retrieving subscription ids from authenticated user...')
        subscriptions_ids = []
        response = dict()

        response['nextPageToken'] = ''
        while 'nextPageToken' in response:
            response = self.OAuth_connection.subscriptions().list(
                part='snippet', mine=True, maxResults=50, pageToken=response['nextPageToken']).execute()
            for item in response['items']:
                subscriptions_ids.append(item['snippet']['resourceId']['channelId'])
        number_of_subscriptions = response['pageInfo']['totalResults']
        print('Number of subscriptions: {}'.format(number_of_subscriptions))
        assert number_of_subscriptions == len(subscriptions_ids)

        return subscriptions_ids

    def get_video_ids_from_channel_ids(self, channel_ids, return_list=True,verbose=False):
        # https: // developers.google.com / youtube / v3 / docs / search / list
        if verbose:
            print('Retrieving video ids for every one of {} channel ids...'.format(len(channel_ids)))
        videos = dict()
        for i, channel_id in enumerate(channel_ids):
            videos[channel_id] = []
            response = dict()
            response['nextPageToken'] = ''
            while 'nextPageToken' in response:
                try:
                    response = self.API_connection.search().list(
                        part='id', channelId=channel_id, maxResults=50,pageToken=response['nextPageToken']).execute()
                except HttpError as e:
                    print(e, channel_id)
                    break
                for item in response['items']:
                    if 'videoId' in item['id']:
                        videos[channel_id].append(item['id']['videoId'])
            if verbose:
                print('{}. {} video ids were retrieved for channel id: {}'.format(i,len(videos[channel_id]),channel_id))
        if return_list:
            videos_list = []
            for k, v in videos.items():
                videos_list.extend(v)
            return videos_list
        else:
            return videos

    def get_comments_from_video_ids(self, video_ids, max_comments_per_video=None, return_list=True,verbose=False):

        # https: // developers.google.com / youtube / v3 / docs / commentThreads / list
        # requests_per_video: each requests returns at most 100 parent comments alongside with some of their replies

        # (Note that a commentThread resource does not necessarily contain all replies to a comment,
        # and you need to use the comments.list method if you want to retrieve all replies for a particular comment.)
        # ---> https: // developers.google.com / youtube / v3 / guides / implementation / comments

        if verbose:
            print('Retrieving comments for every one of {} video ids...'.format(len(video_ids)))
        comments = dict()

        for i, video_id in enumerate(video_ids):
            comments[video_id] = []
            response = dict()
            response['nextPageToken'] = ''
            while 'nextPageToken' in response:
                try:
                    response = self.API_connection.commentThreads().list(
                        part='snippet,replies', videoId=video_id, maxResults=100,
                        textFormat='plainText', pageToken=response['nextPageToken']).execute()
                except HttpError as e:
                    print(e, video_id)
                    break
                comments_for_video = []
                for item in response['items']:
                    comment = item["snippet"]["topLevelComment"]
                    # author = comment["snippet"]["authorDisplayName"]
                    text = comment["snippet"]["textOriginal"]
                    comments_for_video.append(text)
                    if 'replies' in item:
                        replies = item['replies']['comments']
                        for reply in replies:
                            text = reply["snippet"]["textOriginal"]
                            comments_for_video.append(text)
                comments[video_id].extend(comments_for_video)
                if max_comments_per_video is not None:
                    if len(comments[video_id]) >= max_comments_per_video:
                        comments[video_id] = comments[video_id][:max_comments_per_video]
                        break
            if verbose:
                print('{}. {} comments were retrieved for video id: {}'.format(i, len(comments[video_id]), video_id))
        if return_list:
            comments_list = []
            for k, v in comments.items():
                comments_list.extend(v)
            return comments_list
        else:
            return comments

    # NEEDS fixes to return ids
    # User might have private subscription list so this request may throw error
    # def get_subscriptions_list_by_id(self, channel_ids, **kwargs):
    #     # https://developers.google.com/youtube/v3/docs/subscriptions/list
    #     print('Retrieving video ids for every channel id...')
    #     videos = dict()
    #     for channel_id in channel_ids:
    #         response = self.API_connection.subscriptions().list(channelId=channel_id, **kwargs).execute()
    #
    #     return response

    # def channel_information(self, channel_id, retries_if_exception=5, sleep_seconds=5):
    #     for i in range(retries_if_exception):
    #         try:
    #             response = self.connection.channels().list(part='snippet,statistics', id=channel_id).execute()
    #         except Exception as e:
    #             sleep(sleep_seconds)
    #             continue
    #         break
    #     return response

