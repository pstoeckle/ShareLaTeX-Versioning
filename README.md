# ShareLaTeX-Versioning

The idea of this repository is pretty simple.
You are writing your paper using [TUM's ShareLaTeX instance](https://latex.tum.de).
Although ShareLaTeX is cool, you also want to have your paper under git version control.
Here, this tool comes into play.
With this tool, you can download and extract your project with one command.
All the extracted files are automatically marked as read-only so that you are not tempted to directly modify them on your local hard drive.
If you want, you can instruct the script to delete all files which are no longer part of your ShareLaTeX project.
This is especially handy when you delete files in ShareLaTeX and you want them also deleted in your git repository.

## General Setup

1. Install [Python](https://www.python.org/downloads/)
2. Install the package

    ```bash
    pip install sharelatex-versioning --extra-index-url https://__token__:<your_personal_token>@gitlab.lrz.de/api/v4/projects/52151/packages/pypi/simple
    ```

    Now you should be able to call `sharelatex-versioning` within your shell.

## Repository Setup

1. Open your ShareLaTeX project.
5. In the URL field of your browser, the link of your project should look like this.

    ```bash
   https://latex.tum.de/project/this-is-your-project-id
    ```

   Note the `project_id`
6. Create folder named `my_cool_sharelatex_project`
7. Change the directory into the folder
8. Initialize a git repository

    ```bash
    git init
    ```

9. Create a file named `sv_config.json`
10. Open that file and change it to

    ```json
    {
        "project_id": "your_project_id",
        "username": "your LRZ ID",
        "password": "your password",
        "sharelatex_url": "https://latex.tum.de/"
    }
    ```

    Replace the placeholders with your values.

## Creating a commit

1. Run the command

    ```bash
    sharelatex-versioning download-zip --in_file ./sv_config.json
    ```

    Now, you should have a local copy of your ShareLaTeX project.
3. Commit your changes

## Cron

You can also use this tool within a cron job to create every X minute a new commit.

1. Create script file, e.g., `commit.sh`
2. Make it executable

    ```bash
    chmod +x commit.sh
    ```

3. Change the content to the following

    ```bash
    sharelatex-versioning download-zip --in_file /path/to/sv_config.json --working_dir /path/to/repository
    cd /path/to/repository
    git commit -m "Update"
    ```

   Usually, it is better to use the absolute path to the `sharelatex-versioning` script.
   You can get this path by calling

   ```bash
   which sharelatex-versioning
   ```

4. Open cron

    ```bash
    crontab -e
    ```

5. Add this line

   ```cron
   1/10  8-18    *       *       1-5             /path/to/commit.sh >> /path/to/repo/commit.log 2>&1
   ```

    Now, every 10 minute, there will be a commit with the new changes to your ShareLaTeX project.

## Contact

If you have any question, please contact [Patrick Stöckle](mailto:patrick.stoeckle@tum.de).
