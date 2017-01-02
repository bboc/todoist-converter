# todoist-converter

Converter for Todoist CSV templates and projects to Markdown, Taskpaper and OPML, and back from OPML to Todoist CSV.


## Setup

Clone the repository and set it up via 

`python setup.py`


## Usage 

`tdconv <source file name> --format <md|opml|todoist|taskpaper>`

Result will be written to the current folder.

## Migrating projects from Todoist to Taskpaper

Because Todoist cannot export mulitple projects to one file, each Taskpaper file is exported as one project, so that it's easy to combine individual project exports, e.g. via copy and paste in the Taskpaper app or via `cat file1 file2 >destination`

**Known Limitations**:

* due dates might not be recognized correctly by TaskPaper Mac app.
* project notes are not exported by Todoist

### Converting a single project/template

1. Export project as CSV in todoist
    1. Project actions -> Export as template (CSV)
    2. Untick Box "Use relative dates"!!
    3. Export as File
2. `tdconv <source file name> --format taskpaper` 
 

### Full migration

1. Download the latest backup from Todoist (Settings -> Backups)
2. unzip the resulting files
3. `ls -b | xargs -I xx tdconv --format=taskpaper "xx"`


## Notes

Import of generated CSV tested with Todoist on OS-X version 715.


## TODO

- Create a formula for homebrew, see for explanation http://jimkubicek.com/blog/2015/02/14/creating-a-homebrew-formula-for-a-python-project/
