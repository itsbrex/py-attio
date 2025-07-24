import requests


class BaseClient:

	def __init__(self, api_key: str):

		self.base_url = "https://api.attio.com/v2"
		self.api_key = api_key
		self.session = requests.Session()
		self.session.headers.update({
        	"authorization": f"Bearer {self.api_key}",
        	"accept": "application/json",
        	"content-type": "application/json"
		})


	def _request(self, method: str, path: str, **kwargs):

		url = f"{self.base_url}{path}"
		response = self.session.request(method, url, **kwargs)
		if not response.ok:
			raise Exception(f"Request failed: {response.status_code} - {response.text}")
		return response .json()


class Client(BaseClient):

	# Objects

	def get_object(self, object_id):
		return self._request("GET", f"/objects/{object_id}")


	def list_objects(self):
		return self._request("GET", "/objects")


	def create_object(self, payload):
		return self._request("POST", "/objects", json=payload)


	def update_object(self, object_id, payload):
		return self._request("PATCH", f"/objects/{object_id}", json=payload)


	# Attributes

	def list_attributes(self, target, identifier):
		return self._request("GET", f"/{target}/{identifier}/attributes")


	def create_attribute(self, target, identifier, payload):
		return self._request("POST", f"/{target}/{identifier}/attributes")


	def get_attribute(self, target, identifier, attribute):
		return self._request("GET", f"/{target}/{identifier}/attributes/{attribute}")


	def update_attribute(self, target, identifier, attribute, payload):
		return self._request("PATCH", f"/{target}/{identifier}/attributes/{attribute}")


	# Records

	def list_records(self, object_id, params=None):
		return self._request("POST", f"/objects/{object_id}/records/query", params=params)


	def get_record(self, object_id, record_id):
		return self._request("GET", f"/objects/{object_id}/records/{record_id}")


	def create_record(self, object_id, payload):
		return self._request("POST", f"/objects/{object_id}/records")


	def assert_record(self, object_id, payload):
		return self._request("PUT", f"/objects/{object_id}/records")



