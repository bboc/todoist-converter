# todoist-converter

Convert [Todoist](http://todoist.com/) CSV templates and entire Todoist backups to TaskPaper, Markdown, or OPML, and convert OPML-Files back to Todoist CSV templates.

Whether you're ready to move from Todoist to Taskpaper, or if you just want to convert individual projects to opml and back again - e.g. for use in [CarbonFin Outliner](http://carbonfin.com/) or OmniOutliner - todoist-convert has you covered.

Todoist note attachments are either referenced via URL, or optionally downloaded locally (for Markdown or TaskPaper files).

## Get the OS-X App

For the casual user it's highly recommended to download the [MacOS App from github](https://github.com/bboc/todoist-converter/releases/latest)

To see what's new, take a look at the [changelog](#changelog) at the bottom of this file.

## tdconv command

### Setup

Download a [release from github](https://github.com/bboc/todoist-converter/releases) or clone the repository, then set it up for usage via 

`python setup.py install`

or for development with

`make develop`

You might want to set up a virtual environment before you do that.

There's a makefile with several commands that help you building and debugging the Application with [pyinstaller](https://pyinstaller.org)


### Usage

`tdconv <source file name> --format <md|opml|todoist|taskpaper>`

Result will be written to the current folder.

If an output file is specified with `--output` or `-o`, and the output file exists, TaskPaper and MD formats simply append to that file, so the output of multiple files can be combined into one file. 


### Migrating projects from Todoist to Taskpaper

Because Todoist cannot export multiple projects to one file, each Taskpaper file is exported as one project, so that it's easy to combine individual project exports, e.g. via copy and paste in the Taskpaper App or via `cat file1 file2 >destination`

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

Download the latest backup from Todoist (Settings -> Backups) and either use 

`tdconv -df taskpaper <your-backup.zip>`

or manually:

1. unzip the downloaded archive
2. `ls -bp | xargs -I xx tdconv -df taskpaper "xx"`


## Notes

Import of generated CSV tested with Todoist on OS-X version 715.

## Changelog

The format of the changelog is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

### 1.0

- **added**: tabbed GUI for selecting individual files or whole directories
- **added**: App now outputs parameters and output directory before conversion
- **fixed**: App tests for existence of input file before conversion
- **added**: App displays error information
- **added**: App icon
- **added**: App now can process an entire directory todoist- or opml-files
- **added**: App and commandline tools now are able to process an zip file (e.g. the backups downloaded from todoist) in one go
- **added**: App now displays conversion formats dependent on the selected input file
- **fixed**: App defaults to write to root folder on MacOS
- 
- **added**: makefile with commands for building release and debug apps
- **changed**: cleaned up layout of app
- **fixed**: fixed a bug in taskpaper export where empty priority in a task would result in an exception

### 0.3

- **added**: MacOS App with a very simple GUI
- **added**: added `--output`, md and taskpaper formats append output if file is present
