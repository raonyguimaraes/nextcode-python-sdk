"""
Service class
------------------
Service object for interfacing with the Project-Service API

"""

import logging
from typing import Optional, List, Union, Dict
from ...client import Client
from ...services import BaseService

SERVICE_PATH = "api/project"

log = logging.getLogger(__file__)


class Service(BaseService):
    def __init__(self, client: Client, *args, **kwargs) -> None:
        super(Service, self).__init__(client, SERVICE_PATH, *args, **kwargs)

    def list_projects(self) -> List:
        """
        Returns the projects that have been created on the current server

        Refer to the API documentation for the Project service to see formatting of data.

        :return: List of projects
        """
        return self.__get_all_projects()

    def add_project(self, project_config: dict) -> Dict:
        project_endpoint = self.session.url_from_endpoint("projects")
        resp = self.session.post(project_endpoint, json=project_config)
        return resp.json()

    def get_project_by_id(self, project_id: int) -> Dict:
        """
        Returns the projects that have been created on the current server

        Refer to the API documentation for the Project service to see formatting of data.

        :return: A single project
        """
        projects = self.__get_all_projects()
        # TODO: Unwind this horrible mess. Ég sver það, Nonni leyfir mér aldrei að skrifa kóða aftur.
        project = [x['links']['self'] for x in projects if x["project_id"] == project_id]
        if not project:
            raise Exception(f"Project with project_id {project_id} not found.")
        else:
            project_url = project[0]
        resp = self.session.get(project_url)
        project_info = resp.json()
        return project_info

    def __get_all_projects(self) -> List:
        """
        Returns the projects that have been created on the current server

        :return: List of projects
        """
        project_url = self.session.url_from_endpoint("projects")

        return self.session.get(project_url).json()

    def get_users_for_project(self, project_id):
        users_endpoint = self.get_project_by_id(project_id)['links']['users']  # Yeah, I suck :P
        data = dict(project_id=project_id)
        resp = self.session.get(users_endpoint, data=data)
        resp.raise_for_status()
        return resp

    def get_user(self, user_id):
        users_endpoint = self.session.url_from_endpoint("users")
        user = self.session.get(f"{users_endpoint}{user_id}")
        user.raise_for_status()
        return user

    def grant_user_access_to_project(self, project_id, username, policy_type):

        grant_endpoint = self.get_project_by_id(project_id)['links']['users']  # Yeah, I suck :P
        users_endpoint = self.session.url_from_endpoint("users")
        # TODO: The service should accept usernames
        user_id = 0
        users = self.session.get(f"{users_endpoint}")
        for x in users.json():
            if x['user_name'] == username or x['user_id'] == username:
                data = {
                    "user_id":  x['user_id'],
                    "policy_type": policy_type
                }
                grant = self.session.post(grant_endpoint, json=data)
                return grant
        raise Exception("User %s not found." % username)
