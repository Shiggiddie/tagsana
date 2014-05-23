from tagsana.tagsana import Tagsana

from collections import defaultdict
from mock import patch, MagicMock
from nose.tools import eq_

class TestTagsana(object):

    def test_currate_tasks(self):
        tagsana = Tagsana()
        fake_tasks = [
            {'id':'1'},
            {'id':2},
            {'id':3},
            {'id':1},
            {'id':2},
            {'id':'foo'},
            {'id':'foo'}]
        expected = [
            {'id':'1'},
            {'id':2},
            {'id':3},
            {'id':1},
            {'id':'foo'}]
        result = tagsana.currate_tasks(fake_tasks)
        eq_(expected, result)

    @patch('tagsana.tagsana.AsanaAPI.list_projects', MagicMock())
    @patch('tagsana.tagsana.Tagsana.currate_tasks', MagicMock(return_value=[{'id':1},{'id':2},{'id':3},{'id':4},{'id':5},{'id':6},]))
    @patch('tagsana.tagsana.AsanaAPI.get_task_tags', MagicMock(side_effect=[[{'name':'tag1'}],[{'name':'tag1'}],[{'name':'tag2'}],[{'name':'tag3'}],[{'name':'tag3'}],[{'name':'tag3'}]]))
    def test_get_count(self):
        tagsana = Tagsana()
        expected = defaultdict(int)
        expected['tag1'] = 2
        expected['tag2'] = 1
        expected['tag3'] = 3
        result = tagsana.get_count({'id':1234})
        eq_(expected, result)

    @patch('tagsana.tagsana.AsanaAPI.list_projects', MagicMock())
    def test_get_count_wss_not_list(self):
        tagsana = Tagsana()
        expected = defaultdict(int)
        result = tagsana.get_count({'id':1234})
        eq_(expected, result)

    @patch('tagsana.tagsana.AsanaAPI.list_workspaces', MagicMock(return_value=[{'id':'foo'}]))
    @patch('tagsana.tagsana.AsanaAPI.list_tasks', MagicMock())
    def test_get_count_users_not_list(self):
        tagsana = Tagsana()
        expected = defaultdict(int)
        result = tagsana.get_count(users={'id':1234})
        eq_(expected, result)

    @patch('tagsana.tagsana.AsanaAPI.list_workspaces', MagicMock())
    @patch('tagsana.tagsana.AsanaAPI.get_project_tasks', MagicMock())
    def test_get_count_projs_not_list(self):
        tagsana = Tagsana()
        expected = defaultdict(int)
        result = tagsana.get_count(projs={'id':1234})
        eq_(expected, result)
