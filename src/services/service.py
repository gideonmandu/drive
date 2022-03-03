import json
import os

from datetime import datetime
from googleapiclient.discovery import build, Resource
from google.oauth2 import service_account as sa
from typing import List, Dict


class Services:
    """
    Initialize Google Workspace API Services to be used.
    """

    def __init__(self) -> None:
        self.initialized_directory_service = None

    def directory_api_service(self, admin_email: str) -> Resource:
        """
        Create Admin SDK Directory API Resource object.
        :param admin_email: workspace super admin email
        :type admin_email: str
        :return: Directory API Resource Object
        :rtype: Resource
        """
        return self._service_account(
            scopes=json.loads(f"{os.environ.get('DIRECTORY_API_SCOPES')}"),
            serviceName="admin",
            version="directory_v1",
            credentials_path=f"{os.environ.get('CREDENTIALS_FILE')}",
            email=admin_email,
        )

    def drive_api_service(self, user_email: str) -> Resource:
        """
        Create drive API Resource object.
        :param user_email: workspace user email
        :type user_email: str
        :return: drive API Resource Object
        :rtype: Resource
        """
        return self._service_account(
            scopes=json.loads(f"{os.environ.get('DRIVE_SCOPES')}"),
            serviceName="drive",
            version="v3",
            credentials_path=f"{os.environ.get('CREDENTIALS_FILE')}",
            email=user_email,
        )

    def _service_account(
        self,
        scopes: List[str],
        serviceName: str,
        version: str,
        credentials_path: str,
        email: str,
    ) -> Resource:
        """
        Construct a Service Resource for interacting with an API.
        Construct a Resource object for interacting with an API.
        The serviceName and version are the names from the Discovery service.
        :param scopes: Google Workspace API scopes
        :type scopes: list[str]
        :param serviceName: name of the API service.
        :type serviceName: str
        :param version: the version of the API service.
        :type version: str
        :param credentials_path: path to credential file for service account.
        :type credentials_path: str
        :param email: email of user to impersonate
        :type email: str
        :return: Service Account Resource Object
        :rtype: Resource
        """
        credentials = sa.Credentials.from_service_account_file(
            filename=credentials_path, scopes=scopes
        )
        delegate_cred = credentials.with_subject(subject=email)

        return build(
            serviceName=serviceName,
            version=version,
            credentials=delegate_cred,
        )


services = Services()
