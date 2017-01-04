# todoist-converter

Convert Todoist CSV templates and entire Todoist backup TaskPaper, Markdown, or OPML, and convert OPML-Files to Todoist CSV templates.

Wheter you're ready to move from Todoist to Taskpaper, or if you just want to convert individual projects to opml and back again - e.g. for use in [CarbonFin Outliner](http://carbonfin.com/) or OmniOutliner - todoist-convert has you covered.

Todoist note attachments are either referenced via URL, or optionally downloaded locally (for Markdown or TaskPaper files).


## Get the OS-X App

Download a [release on github](https://github.com/bboc/todoist-converter/releases/latest)


## tdconv command

### Setup

Download a [release from github](https://github.com/bboc/todoist-converter/releases) or clone the repository, then set it up via 

`python setup.py`


### Usage

`tdconv <source file name> --format <md|opml|todoist|taskpaper>`

Result will be written to the current folder.

If an output file is specified with `--output` or `-o`, and the output file exists, TaskPaper and MD formats simply append to that file, so the output of multiple files can be combined into one file. 


### Migrating projects from Todoist to Taskpaper

Because Todoist cannot export mulitple projects to one file, each Taskpaper file is exported as one project, so that it's easy to combine individual project exports, e.g. via copy and paste in the Taskpaper app or via `cat file1 file2 >destination`

**Known Limitations**:

* due dates might not be recognized correctly by TaskPaper Mac app.
* project notes are not exported by Todoist


#### Converting a single project/template

1. Export project as CSV in todoist
    1. Project actions -> Export as template (CSV)
    2. Untick Box "Use relative dates"!!
    3. Export as File
2. `tdconv <source file name> --format taskpaper` 
 

#### Full migration

1. Download the latest backup from Todoist (Settings -> Backups)
2. unzip the resulting files
3. `ls -bp | xargs -I xx tdconv -df taskpaper "xx"`


## Notes

Import of generated CSV tested with Todoist on OS-X version 715.
