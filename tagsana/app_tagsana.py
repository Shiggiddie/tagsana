import json
import os
import sqlite3

from itertools import chain

from flask import Flask, request, session, g, redirect, url_for, \
                  abort, render_template, flash
from tagsana import Tagsana

app = Flask(__name__)
app.config.from_object(__name__)
tagsana = Tagsana()

app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'app_tagsana.db'),
    DEBUG=True,
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))
app.config.from_envvar('TAGSANA_SETTINGS', silent=True)

def connect_db():
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

def is_subset(thing, other_thing):
    value = {
        'tag':0,
        'task': 1,
        'project':2,
        'workspace':3}
    if value[thing] < value[other_thing]:
        return True
    else:
        return False

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

@app.route('/')
def main():
    wss = tagsana.api.list_workspaces()
    db = get_db()
    for ws in wss:
        db.execute('INSERT OR REPLACE INTO workspace (id, name) VALUES (?, ?)',
                        [ws['id'], ws['name']])
        db.commit()
    return redirect(url_for('show_workspaces'))

@app.route('/add_tags', methods=['POST'])
def get_tags():
    db = get_db()
    workspace_id = project_id  = task_id = None
    try:
        workspace_id = int(request.form['Workspace'])
    except:
        pass
    else:
        print 'Calling "get_tags" API for workspace: %s...' % (workspace_id,)
        session['workspace_id'] = workspace_id
        tags = tagsana.api.get_tags(workspace_id)
    try:
        project_id = int(request.form['Project'])
    except:
        pass
    else:
        print 'Calling "get_tags" API for project: %s...' % (project_id,)
        session['project_id'] = project_id
        tags = [l for el in [tagsana.api.get_task_tags(t['id'])
                  for t in tagsana.api.get_project_tasks(project_id)]
                  for l in chain(el)]
        print 'API call returned tags: %s' % (tags,)
    try:
        task_id = int(request.form['Task'])
    except:
        AssertionError('No context for searching for tags given!')
    else:
        print 'Calling "get_tags" API for task: %s...' % (task_id,)
        session['task_id'] = task_id
        tags = tagsana.api.get_task_tags(task_id)
    print 'API call returned tags: %s' % (tags,)
    for tag in tags:
        db.execute('INSERT OR REPLACE INTO tag (id, name) VALUES (?, ?)',
                    [tag['id'], tag['name']])
        db.commit()
        if workspace_id:
            db.execute('INSERT OR REPLACE INTO workspace_tag (workspace_id, tag_id) VALUES (?, ?)',
                        [workspace_id, tag['id']])
        elif project_id:
            db.execute('INSERT OR REPLACE INTO project_tag (project_id, tag_id) VALUES (?, ?)',
                        [project_id, tag['id']])
        else:
            db.execute('INSERT OR REPLACE INTO task_tag (task_id, tag_id) VALUES (?, ?)',
                        [task_id, tag['id']])
        print 'addition of tag relationship: %s SUCCESSFUL' % tag
        db.commit()
    return redirect(url_for('show_tags'))

@app.route('/tags')
def show_tags():
    db = get_db()
    context = []
    ct = {}
    if 'workspace_id' in session.keys():
        cur = db.execute("""SELECT tag.id, tag.name
                            FROM tag, workspace, workspace_tag
                            WHERE tag.id = workspace_tag.tag_id
                                AND workspace_tag.workspace_id = workspace.id
                                AND workspace.id = (?)""", [session['workspace_id']])
        ct_cur = db.execute('SELECT name FROM workspace WHERE workspace.id = (?)', [session['workspace_id']])
        ct['type'] = 'workspace'
        session.pop('workspace_id')
    elif 'project_id' in session.keys():
        cur = db.execute("""SELECT tag.id, tag.name
                            FROM tag, project, project_tag
                            WHERE tag.id = project_tag.tag_id
                                AND project_tag.project_id = project.id
                                AND project.id = (?)""", [session['project_id']])
        ct_cur = db.execute('SELECT name FROM project WHERE project.id = (?)', [session['project_id']])
        ct['type'] = 'project'
        session.pop('project_id')
    elif 'task_id' in session.keys():
        cur = db.execute("""SELECT tag.id, tag.name
                            FROM tag, task, task_tag
                            WHERE tag.id = task_tag.tag_id
                                AND task_tag.task_id = task.id
                                AND task.id = (?)""", [session['task_id']])
        ct_cur = db.execute('SELECT name FROM task WHERE task.id = (?)', [session['task_id']])
        ct['type'] = 'task'
        session.pop('task_id')
    else:
        cur = db.execute('SELECT id, name FROM tag')
    if ct:
        ct['name'] = ct_cur.fetchone()['name']
        ct['prep'] = 'in' if is_subset('tag', ct['type']) else 'for'
        context.append(ct)
    entries = cur.fetchall()
    return render_template('show_entries.html', entries=entries, entry_type='Tag', context=context)

@app.route('/add_tasks', methods=['POST'])
def get_tasks():
    db = get_db()
    workspace_id = project_id  = tag_id = None
    try:
        workspace_id = int(request.form['Workspace'])
    except:
        pass
    else:
        session['workspace_id'] = workspace_id
        print 'Calling "get_project_tasks" API for workspace: %s...' % (workspace_id,)
        projects = tagsana.api.list_projects(workspace_id)
        print 'Calling "get_project_tasks" API for projects: %s...' % (projects,)
        tasks = [l for el in [tagsana.api.get_project_tasks(p) 
                                for proj in projects 
                                for k, p in proj.iteritems() 
                                if k == 'id'] for l in chain(el)]
    try:
        project_id = int(request.form['Project'])
    except:
        pass
    else:
        session['project_id'] = project_id
        print 'Calling "get_project_tasks" API for project: %s...' % (project_id,)
        tasks = tagsana.api.get_project_tasks(project_id)
    try:
        tag_id = int(request.form['Tag'])
    except:
        AssertionError('No context for searching for projects given!')
    else:
        session['tag_id'] = tag_id
        print 'Calling "get_tag_tasks" API for tag: %s...' % (tag_id,)
        tasks = tagsana.api.get_tag_tasks(tag_id)
    print 'API call returned tasks: %s' % (tasks,)
    for task in tasks:
        db.execute('INSERT OR REPLACE INTO task (id, name) VALUES (?, ?)',
                    [task['id'], task['name']])
        print 'addition of task: %s SUCCESSFUL' % task
        db.commit()
        if workspace_id:
            db.execute('INSERT OR REPLACE INTO workspace_task (workspace_id, task_id) VALUES (?, ?)',
                        [workspace_id, task['id']])
        elif project_id:
            db.execute('INSERT OR REPLACE INTO project_task (project_id, task_id) VALUES (?, ?)',
                        [project_id, task['id']])
        else:
            db.execute('INSERT OR REPLACE INTO task_tag (task_id, tag_id) VALUES (?, ?)',
                        [task['id'], tag_id])
        print 'addition of task relationship: %s SUCCESSFUL' % task
        db.commit()
    return redirect(url_for('show_tasks'))

@app.route('/tasks')
def show_tasks():
    db = get_db()
    context = []
    ct = {}
    if 'workspace_id' in session.keys():
        cur = db.execute("""SELECT task.id, task.name
                            FROM task, workspace, workspace_task
                            WHERE task.id = workspace_task.task_id
                                AND workspace_task.workspace_id = workspace.id
                                AND workspace.id = (?)""", [session['workspace_id']])
        ct_cur = db.execute('SELECT name FROM workspace WHERE workspace.id = (?)', [session['workspace_id']])
        ct['type'] = 'workspace'
        session.pop('workspace_id')
    elif 'project_id' in session.keys():
        cur = db.execute("""SELECT task.id, task.name
                            FROM task, project, project_task
                            WHERE task.id = project_task.task_id
                                AND project_task.project_id = project.id
                                AND project.id = (?)""", [session['project_id']])
        ct_cur = db.execute('SELECT name FROM project WHERE project.id = (?)', [session['project_id']])
        ct['type'] = 'project'
        session.pop('project_id')
    elif 'tag_id' in session.keys():
        cur = db.execute("""SELECT task.id, task.name
                            FROM task, tag, task_tag
                            WHERE task.id = task_tag.task_id
                                AND task_tag.tag_id = tag.id
                                AND tag.id = (?)""", [session['tag_id']])
        ct_cur = db.execute('SELECT name FROM tag WHERE tag.id = (?)', [session['tag_id']])
        ct['type'] = 'tag'
        session.pop('tag_id')
    else:
        cur = db.execute('SELECT id, name FROM task')
    if ct:
        ct['name'] = ct_cur.fetchone()['name']
        ct['prep'] = 'in' if is_subset('task', ct['type']) else 'for'
        context.append(ct)
    entries = cur.fetchall()
    return render_template('show_entries.html', entries=entries, entry_type='Task', context=context)

@app.route('/add_projects', methods=['POST'])
def get_projects():
    db = get_db()
    workspace_id = task_id = tag_id = None

    #Workflow for discovering projects when workspace is known
    try:
        workspace_id = int(request.form['Workspace'])
    except:
        pass
    else:
        session['workspace_id'] = workspace_id
        print 'Calling "list_projects" API for workspace: %s...' % (workspace_id,)
        projects = tagsana.api.list_projects(workspace_id)
        print 'Calling "get_project_tasks" API for projects: %s...' % (projects,)

    #Workflow for discovering projects when task is known
    try:
        task_id = int(request.form['Task'])
    except:
        pass
    else:
        session['task_id'] = task_id
        print 'Calling "get_task" API for task: %s...' % (task_id,)
        projects = tagsana.api.get_task(task_id)['projects']

    #Workflow for discovering projects when tag is known
    try:
        tag_id = int(request.form['Tag'])
    except:
        AssertionError('No context for searching for projects given!')
    else:
        session['tag_id'] = tag_id
        print 'Calling "get_tag_tasks" API for tag: %s...' % (tag_id,)
        projects = []
        workspace_ids = [ws['id'] for ws in tagsana.api.list_workspaces()]
        projs = [p for el in [tagsana.api.list_projects(w) for w in workspace_ids] for p in chain(el)]
        for proj in projs:
            print 'Looking at tasks in proj: %s' % proj
            for task in tagsana.api.get_project_tasks(proj['id']):
                print 'Looking at task: %s' % task
                if any([tag_id == tag.get('id') for tag in tagsana.api.get_task(task['id']).get('tags',[])]):
                    print 'FOUND A TAG THAT MATCHED tag_id!'
                    projects.append(proj)
                    break

    #Now that projects have been discovered, add them to the DB
    print 'API call returned projects: %s' % (projects,)
    for project in projects:
        db.execute('INSERT OR REPLACE INTO project (id, name) VALUES (?, ?)',
                    [project['id'], project['name']])
        print 'addition of project: %s SUCCESSFUL' % project
        db.commit()
        if workspace_id:
            db.execute('INSERT OR REPLACE INTO workspace_project (workspace_id, project_id) VALUES (?, ?)',
                        [workspace_id, project['id']])
        elif task_id:
            db.execute('INSERT OR REPLACE INTO project_task (project_id, task_id) VALUES (?, ?)',
                        [project['id'], task_id])
        else:
            db.execute('INSERT OR REPLACE INTO project_tag (project_id, tag_id) VALUES (?, ?)',
                        [project['id'], tag_id])
        print 'addition of project relationship: %s SUCCESSFUL' % project
        db.commit()
    return redirect(url_for('show_projects'))


@app.route('/projects')
def show_projects():
    db = get_db()
    context = []
    ct = {}
    if request.args:
        print 'request.args: %s\n\n\n' % request.args
    else:
        print 'no request.args'
    if 'workspace_id' in session.keys():
        cur = db.execute("""SELECT project.id, project.name
                            FROM project, workspace, workspace_project
                            WHERE project.id = workspace_project.project_id
                                AND workspace_project.workspace_id = workspace.id
                                AND workspace.id = (?)""", [session['workspace_id']])
        ct_cur = db.execute('SELECT name FROM workspace WHERE workspace.id = (?)', [session['workspace_id']])
        ct['type'] = 'workspace'
        session.pop('workspace_id')
    elif 'task_id' in session.keys():
        cur = db.execute("""SELECT project.id, project.name
                            FROM task, project, project_task
                            WHERE project.id = project_task.project_id
                                AND project_task.task_id = task.id
                                AND task.id = (?)""", [session['task_id']])
        ct_cur = db.execute('SELECT name FROM task WHERE task.id = (?)', [session['task_id']])
        ct['type'] = 'task'
        session.pop('task_id')
    elif 'tag_id' in session.keys():
        cur = db.execute("""SELECT project.id, project.name
                            FROM project, tag, project_tag
                            WHERE project.id = project_tag.project_id
                                AND project_tag.tag_id = tag.id
                                AND tag.id = (?)""", [session['tag_id']])
        ct_cur = db.execute('SELECT name FROM tag WHERE tag.id = (?)', [session['tag_id']])
        ct['type'] = 'tag'
        session.pop('tag_id')
    else:
        cur = db.execute('SELECT id, name FROM project')
    if ct:
        ct['name'] = ct_cur.fetchone()['name']
        ct['prep'] = 'in' if is_subset('project', ct['type']) else 'for'
        context.append(ct)
    entries = cur.fetchall()
    return render_template('show_entries.html', entries=entries, entry_type='Project', context=context)

@app.route('/query/')
def show_by_query_string():
    db = get_db()

    def create_sql_srq(srq, rt):
        #Determine the table to be queried
        qt = srq.pop('qt')

        #Determine the query type
        qtype = srq.keys()[0]

        #Grab the ids to be queried
        ids = ', '.join([str(v) for v in srq[qtype]])

        #Construct the relationship table
        if is_subset(rt, qt):
            relt = '%s_%s' % (qt, rt)
        else:
            relt = '%s_%s' % (rt, qt)

        _base = 'SELECT %s_id FROM %s WHERE %s_id IN (%s)' % (rt, relt, qt, ids)

        if any(qtype == q for q in ['only','all']):
            _all = ' GROUP BY %s_id HAVING count(%s_id) == %s' % (rt, rt, len(srq[qtype]))
        else:
            _all = ''

        if qtype == 'only':
            _s_only = 'SELECT %s_id FROM %s WHERE %s_id IN (' % (rt, relt, rt)
            _e_only = ') GROUP BY %s_id HAVING count(%s_id) == %s' % (rt, qt, len(srq[qtype]))
        else:
            _s_only = ''
            _e_only = ''

        return _s_only + _base + _all + _e_only

    def create_sql_srqs(srqs, rt):
        sql_srqs = []
        for srq in srqs:
            sql_srqs.append(create_sql_srq(srq, rt))
        return sql_srqs

    def create_sql_crqs(crq_type, sql_srqs, rt, sql_crqs):
        if crq_type == 'or':
            s_crq = ' UNION ALL '
            e_crq = ''
        else:
            s_crq = ' AND %s_id IN(' % rt
            e_crq = ')'

        for sql_srq in sql_srqs:
            if sql_crqs:
                sql_crqs += s_crq + sql_srq + e_crq
            else:
                sql_crqs += sql_srq

        return sql_crqs

    query = json.loads(request.args.get('query'))
    rtvs = query.pop('rt')
    rt = rtvs.keys()[0]
    cols = ', '.join(rtvs[rt])
    query_start = 'SELECT %s FROM %s WHERE id IN(' % (cols, rt)
    sql_crqs = ''
    for crq_type, srqs in query.iteritems():
        sql_srqs = create_sql_srqs(srqs, rt)
        sql_crqs = create_sql_crqs(crq_type, sql_srqs, rt, sql_crqs)
    sql_query = query_start + sql_crqs + ');'

    #sql_query = sql_select + tables + ands
    print 'About to Query: %s' % sql_query
    cur = db.execute(sql_query)
    entries = cur.fetchall()
    #print 'Context is currently: %s' % context
    return render_template('show_entries.html', entries=entries, entry_type=rt.capitalize())
    return render_template('show_entries.html', entries=entries, entry_type=qt.capitalize(), context=context)

@app.route('/workspaces')
def show_workspaces():
    db = get_db()
    cur = db.execute('SELECT id, name FROM workspace')
    entries = cur.fetchall()
    return render_template('show_entries.html', entries=entries, entry_type='Workspace')

if __name__ == '__main__':
    app.run(host='0.0.0.0')
