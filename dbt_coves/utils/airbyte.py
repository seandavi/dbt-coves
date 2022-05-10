import json
from itertools import product
from typing import Dict, Optional, Union

import requests
from requests.exceptions import RequestException

AIRBYTE_ENTITIES = [
    "destination_definitions",
    "source_definitions",
    "destination_definition_specifications",
    "source_definition_specifications",
    "connections",
    "sources",
    "destinations",
    "workspaces",
]


class AirbyteException(Exception):
    pass


class DictAttrMixin(object):
    def __getitem__(self, name):
        return getattr(self, name)

    def __setitem__(self, name, value):
        setattr(self, name, value)

    def __delitem__(self, name):
        delattr(self, name)


class AirbyteAPI(DictAttrMixin):
    def __init__(self, api_host: str, api_port: Union[str, int]):
        airbyte_host = api_host
        airbyte_port = api_port
        airbyte_api_root = "api/v1/"

        airbyte_api_base_endpoint = f"{airbyte_host}:{airbyte_port}/{airbyte_api_root}"

        for resource, verb in product(
            AIRBYTE_ENTITIES,
            (
                "list",
                "get",
                "delete",
                "update",
                "create",
            ),
        ):
            self[
                f"airbyte_endpoint_{verb}_{resource if verb != 'get' else resource[:-1]}"
            ] = f"{airbyte_api_base_endpoint}/{resource}/{verb}"

        try:
            self.airbyte_workspace_id = self.call(
                self["airbyte_endpoint_list_workspaces"]
            )["workspaces"][0]["workspaceId"]

            self.standard_request_body = {"workspaceId": self.airbyte_workspace_id}

            self.airbyte_connections_list = self.call(
                self.airbyte_endpoint_list_connections, self.standard_request_body
            )["connections"]
            self.airbyte_sources_list = self.call(
                self.airbyte_endpoint_list_sources, self.standard_request_body
            )["sources"]
            self.airbyte_destinations_list = self.call(
                self.airbyte_endpoint_list_destinations, self.standard_request_body
            )["destinations"]

            self.load_definitions()
        except AirbyteException as exc:
            raise AirbyteException(
                f"Operation failed during retrieval Airbyte connections, sources, and destinations {str(exc)}"
            ) from exc

    def load_definitions(self) -> None:
        self.destination_definitions = self.call(
            self["airbyte_endpoint_list_destination_definitions"],
            self.standard_request_body,
        )["destinationDefinitions"]

        self.source_definitions = self.call(
            self["airbyte_endpoint_list_source_definitions"],
            self.standard_request_body,
        )["sourceDefinitions"]

    def call(
        self, endpoint: str, body: Optional[Dict[str, str]] = None
    ) -> Dict[str, str]:
        """
        Generic `api caller` for contacting Airbyte
        """
        try:
            response = requests.post(endpoint, json=body)
            if response.status_code >= 200 and response.status_code < 300:
                return json.loads(response.text) if response.text else None
            else:
                raise RequestException(
                    f"Unexpected status code from airbyte in endpoint {endpoint}: {response.status_code}: {json.loads(response.text)['message']}"
                )
        except RequestException as exc:
            raise AirbyteException(
                f"Airbyte API error in endpoint {endpoint}: {str(exc)}"
            ) from exc
