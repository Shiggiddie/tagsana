CREATE TABLE tag (
    id INTEGER PRIMARY KEY,-- task(s) ???,-- project(s) ???,-- dates(s) ???
    name TEXT NOT NULL    
);

CREATE TABLE task (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    -- tag(s) ???,
    -- project(s) ???,
    notes TEXT,
    completed BOOLEAN,
    completed_at TEXT,
    due_on TEXT,
    created_at TEXT
);

CREATE TABLE project (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
    -- tasks ???,
    -- workspaces ???
);

CREATE TABLE workspace (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE workspace_tag (
    workspace_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    UNIQUE (workspace_id, tag_id)
);

CREATE TABLE project_tag (
    project_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    UNIQUE (project_id, tag_id)
);

CREATE TABLE task_tag (
    task_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    UNIQUE (task_id, tag_id)
);

CREATE TABLE workspace_task (
    workspace_id INTEGER NOT NULL,
    task_id INTEGER NOT NULL,
    UNIQUE (workspace_id, task_id)
);

CREATE TABLE project_task (
    project_id INTEGER NOT NULL,
    task_id INTEGER NOT NULL,
    UNIQUE (project_id, task_id)
);

CREATE TABLE workspace_project (
    workspace_id INTEGER NOT NULL,
    project_id INTEGER NOT NULL,
    UNIQUE (workspace_id, project_id)
);
