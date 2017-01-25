import urllib
import urllib.request
import urllib.error
import json


class Trivia:

    def __init__(self):
        self.base_url = "http://jservice.io/api"
        self.current = None

    @staticmethod
    def api_request(url):
        req = urllib.request.Request(url)

        try:
            response = urllib.request.urlopen(req)
            raw_data = response.read()
            data = json.loads(raw_data.decode("utf-8"))
        except urllib.error.HTTPError as err:
            print("API Request Error: {0}".format(err))
            raise UserWarning

        return data

    def get_trivia_question(self):
        endpoint = '/random'

        data = self.api_request("{}{}".format(self.base_url, endpoint))
        self.current = data[0]

        return self.current

    def get_trivia_answer(self):
        answer = None

        if self.current:
            answer = self.current['answer']

        self.current = None

        return answer

