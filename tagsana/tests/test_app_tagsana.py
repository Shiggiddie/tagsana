import tagsana.app_tagsana as tagapp

import os
import tempfile

from mock import patch, MagicMock

class TestAppTagsana(object):

    def setUp(self):
        self.db_fd, tagapp.app.config['DATABASE'] = tempfile.mkstemp()
        tagapp.app.config['TESTING'] = True
        self.app = tagapp.app.test_client()
        tagapp.init_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(tagapp.app.config['DATABASE'])

    def test_resolve_index(self):
        rv = self.app.get('/')
        assert 'Redirecting...' in rv.data
        rv = self.app.get('/', follow_redirects=True)
        assert 'Workspaces' in rv.data

    @patch('tagsana.app_tagsana.tagsana.api.list_workspaces', MagicMock(return_value=[]))
    def test_no_workspaces(self):
        rv = self.app.get('/workspaces')
        assert 'Workspace' in rv.data

    @patch('tagsana.app_tagsana.tagsana.api.list_workspaces', MagicMock(return_value=[{'id':1,'name':'foo'}]))
    def test_one_workspaces(self):
        rv = self.app.get('/', follow_redirects=True)
        assert 'Workspace' in rv.data

    @patch('tagsana.app_tagsana.tagsana.api.list_workspaces', MagicMock(return_value=[{'id':1,'name':'foo'},{'id':2,'name':'boo'}]))
    def test_multi_workspaces(self):
        rv = self.app.get('/', follow_redirects=True)
        assert 'Workspaces' in rv.data

    @patch('tagsana.app_tagsana.tagsana.api.list_workspaces', MagicMock(return_value=[{'id':1,'name':'foo'}]))
    @patch('tagsana.app_tagsana.tagsana.api.get_tags', MagicMock(return_value=[{'id':1,'name':'foo'},{'id':2,'name':'boo'}]))
    def test_add_projects_when_tags_more_than_one(self):
        #Adds Workspace to DB
        rv = self.app.get('/', follow_redirects=True)

        rv = self.app.post('/add_tags',
                           data=dict(Workspace='1'),
                           follow_redirects=True)
        assert 'Tags' in rv.data

    @patch('tagsana.app_tagsana.tagsana.api.list_workspaces', MagicMock(return_value=[{'id':1,'name':'foo'}]))
    @patch('tagsana.app_tagsana.tagsana.api.get_tags', MagicMock(return_value=[{'id':1,'name':'foo'}]))
    def test_add_projects_when_tags_just_one(self):
        #Adds Workspace to DB
        rv = self.app.get('/', follow_redirects=True)

        rv = self.app.post('/add_tags',
                           data=dict(Workspace='1'),
                           follow_redirects=True)
        assert 'Tag' in rv.data

    @patch('tagsana.app_tagsana.tagsana.api.list_workspaces', MagicMock(return_value=[{'id':1,'name':'foo'}]))
    @patch('tagsana.app_tagsana.tagsana.api.get_tags', MagicMock(return_value=[]))
    def test_add_projects_when_tags_none(self):
        #Adds Workspace to DB
        rv = self.app.get('/', follow_redirects=True)

        rv = self.app.post('/add_tags',
                           data=dict(Workspace='1'),
                           follow_redirects=True)
        assert 'Tag' in rv.data

    @patch('tagsana.app_tagsana.tagsana.api.list_workspaces', MagicMock(return_value=[{'id':1,'name':'foo'}]))
    @patch('tagsana.app_tagsana.tagsana.api.list_projects', MagicMock(return_value=[{'id':1,'name':'foo'}]))
    @patch('tagsana.app_tagsana.tagsana.api.get_project_tasks', MagicMock(return_value=[{'id':1,'name':'foo'},{'id':2,'name':'boo'}]))
    def test_add_tasks_when_tasks_more_than_one(self):
        #Adds Workspace to DB
        rv = self.app.get('/', follow_redirects=True)

        rv = self.app.post('/add_tasks',
                           data=dict(Workspace='1'),
                           follow_redirects=True)
        assert 'Tasks' in rv.data

    @patch('tagsana.app_tagsana.tagsana.api.list_workspaces', MagicMock(return_value=[{'id':1,'name':'foo'}]))
    @patch('tagsana.app_tagsana.tagsana.api.list_projects', MagicMock(return_value=[{'id':1,'name':'foo'}]))
    @patch('tagsana.app_tagsana.tagsana.api.get_project_tasks', MagicMock(return_value=[{'id':1,'name':'foo'}]))
    def test_add_tasks_when_tasks_just_one(self):
        #Adds Workspace to DB
        rv = self.app.get('/', follow_redirects=True)

        rv = self.app.post('/add_tasks',
                           data=dict(Workspace='1'),
                           follow_redirects=True)
        assert 'Task' in rv.data

    @patch('tagsana.app_tagsana.tagsana.api.list_workspaces', MagicMock(return_value=[{'id':1,'name':'foo'}]))
    @patch('tagsana.app_tagsana.tagsana.api.list_projects', MagicMock(return_value=[{'id':1,'name':'foo'}]))
    @patch('tagsana.app_tagsana.tagsana.api.get_project_tasks', MagicMock(return_value=[]))
    def test_add_tasks_when_tasks_none(self):
        #Adds Workspace to DB
        rv = self.app.get('/', follow_redirects=True)

        rv = self.app.post('/add_tasks',
                           data=dict(Workspace='1'),
                           follow_redirects=True)
        assert 'Task' in rv.data

    @patch('tagsana.app_tagsana.tagsana.api.list_workspaces', MagicMock(return_value=[{'id':1,'name':'foo'}]))
    @patch('tagsana.app_tagsana.tagsana.api.list_projects', MagicMock(return_value=[{'id':1,'name':'foo'},{'id':2,'name':'boo'}]))
    def test_add_tags_when_tags_more_than_one(self):
        #Adds Workspace to DB
        rv = self.app.get('/', follow_redirects=True)

        rv = self.app.post('/add_projects',
                           data=dict(Workspace='1'),
                           follow_redirects=True)
        assert 'Projects' in rv.data

    @patch('tagsana.app_tagsana.tagsana.api.list_workspaces', MagicMock(return_value=[{'id':1,'name':'foo'}]))
    @patch('tagsana.app_tagsana.tagsana.api.list_projects', MagicMock(return_value=[{'id':1,'name':'foo'}]))
    def test_add_tags_when_tags_just_one(self):
        #Adds Workspace to DB
        rv = self.app.get('/', follow_redirects=True)

        rv = self.app.post('/add_projects',
                           data=dict(Workspace='1'),
                           follow_redirects=True)
        assert 'Project' in rv.data

    @patch('tagsana.app_tagsana.tagsana.api.list_workspaces', MagicMock(return_value=[{'id':1,'name':'foo'}]))
    @patch('tagsana.app_tagsana.tagsana.api.list_projects', MagicMock(return_value=[]))
    def test_add_tags_when_tags_none(self):
        #Adds Workspace to DB
        rv = self.app.get('/', follow_redirects=True)

        rv = self.app.post('/add_projects',
                           data=dict(Workspace='1'),
                           follow_redirects=True)
        assert 'Project' in rv.data
