from datetime import datetime
import os

import asana


def meta_from_name():
    client = asana.Client.access_token(os.environ['ASANA_ACCESS_TOKEN'])
    me = client.users.me()
    for ws_ in client.workspaces.find_all():
        ws = AsanaWorkspace(ws_, me, client)
        ws.set_metadata_from_name()


class AsanaWorkspace(object):

    def __init__(self, ws, me, client):
        self.id = ws['id']
        self.user_id = me['id']
        self.client = client

        self.all_projects = list(client.projects.find_by_workspace(ws['id']))
        self.all_tags = list(client.tags.find_by_workspace(ws['id']))

        self.all_tasks = client.tasks.find_all(params={
            'workspace': self.id,
            'assignee': self.user_id,
            'completed_since': datetime.now().isoformat()
        })

    def set_metadata_from_name(self):
        for t in self.all_tasks:
            try:
                task = AsanaTask(t, self, self.client)
                task.process()
            except Exception as exc:
                print("Cannot process task {}: {}".format(t['id'], exc))

    def get_or_create_project_id(self, project_name):
        print("Creating project '{}'".format(project_name))
        return self.get_or_create_resource(
            project_name, self.all_projects, self.client.projects.create)['id']

    def get_or_create_tag_id(self, tag):
        print("Creating tag '{}'".format(tag))
        return self.get_or_create_resource(
            tag, self.all_tags, self.client.tags.create)['id']

    def get_or_create_resource(self, name, collection, creation_fn):
        if name not in [i['name'] for i in collection]:
            collection.append(creation_fn({'workspace': self.id, 'name': name}))
        return [i for i in collection if i['name'] == name][0]


class AsanaTask(object):

    COMMAND_SEPARATOR = ':'

    def __init__(self, task, workspace, client):
        self.id = task['id']
        self.orig_name = task['name']
        self.workspace = workspace
        self.client = client

        self.target_status = None
        self.target_name = None
        self.commands = []
        self.handlers = {
            't': self.add_tag,
            'p': self.add_to_project,
            's': self.update_status,
        }

        self.parse_task_name()

    def parse_task_name(self):
        """Split off metadata from task name."""
        split_task_name = self.orig_name.split(" ")
        for token in [
            t for t in split_task_name[:]
            if len(t) > 1 and t[1] == self.COMMAND_SEPARATOR
        ]:
            if token[0] in self.handlers.keys():
                self.commands.append(tuple(token.split(self.COMMAND_SEPARATOR)))
                split_task_name.remove(token)
        self.target_name = " ".join(split_task_name)

    def process(self):
        [self.handlers[k](v) for k, v in self.commands]
        if self.commands:
            self.rename_task()

    def add_to_project(self, project_name):
        project_id = self.workspace.get_or_create_project_id(project_name)
        self.client.tasks.add_project(self.id, {'project': project_id})
        print("Task {} in project '{}'".format(
            self.id, project_name))

    def add_tag(self, tag):
        tag_id = self.workspace.get_or_create_tag_id(tag)
        self.client.tasks.add_tag(self.id, {'tag': tag_id})
        print("Task {} tagged '{}'".format(self.id, tag))

    def update_status(self, status):
        self.client.tasks.update(
            self.id, {"assignee_status": status})
        print("Task {}: set status to '{}'".format(self.id, status))

    def rename_task(self):
        self.client.tasks.update(
            self.id, {'name': self.target_name})
        print("Renamed {} from '{}' to '{}'".format(
            self.id, self.orig_name, self.target_name))


import unittest


class AsanaTaskTest(unittest.TestCase):
    def test_parse_name_happy(self):
        in_ = {'name': 'foo t:bar t:baz p:qux s:later', 'id': 'irrelevant'}
        task = AsanaTask(in_, None, None)
        self.assertEqual(
            task.commands,
            [('t', 'bar'), ('t', 'baz'), ('p', 'qux'), ('s', 'later')])
        self.assertEqual(task.target_name, 'foo')
