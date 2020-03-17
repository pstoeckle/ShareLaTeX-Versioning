# Sharelatex-Versioning

The idea of this repository is pretty simple.
You are writing your paper using [TUM's ShareLaTeX instance](https://sharelatex.tum.de).
Although ShareLaTeX is cool, you also want to have your paper under git version control.
Here, this tool comes into play.
With this tool, you can download and extract your project with one command.
All the extracted files are automatically marked as read-only so that you are not tempted to directly modify them on your local hard drive.
If you want, you can instruct the script to delete all files which are no longer part of your ShareLaTeX project.
This is especially handy when you delete files in ShareLaTeX and you want them also deleted in your git repository.

## General Setup

1. Install [Python](https://www.python.org/downloads/)
2. Clone this repository
3. Navigate to the path of this repository
4. Install all its dependencies.

    ```bash
    pip install -r requirements.txt
    ```

5. Install the command-line script

    ```bash
    pip install -e . 
    ```

    Now you should be able to call `sharelatex-versioning` within your shell.
    
## Repository Setup

1. Open your ShareLaTeX project.
2. Click on `Share`
3. Click on `Turn on link sharing`
4. You should see link

    ```
    https://sharelatex.tum.de/read/this_is_your_share_id
    ```
   
    Note the `share_id`.
5. In the URL field of your browser, the link of your project should look like this.

    ```
   https://sharelatex.tum.de/project/this-is-your-project-id
    ```
   Note the `project_id`
6. Create folder named `my_cool_sharelatex_project`
7. Change the directory into the folder
8. Initialize a git repository
   
    ```bash
    git init
    ```
   
9. Create a file named `config.json`
10. Open that file and change it to
    
    ```json
    {
      "share_id": "your_share_id",
      "project_id": "your_project_id"
    }
    ```
    
    Replace the placeholders with your values.

## Creating a commit  

1. Run the command

    ```bash
    sharelatex-versioning download-zip --in_file ./config.json
    ```
    
    Now, you should have a local copy of your ShareLaTeX project.
2. Add all files to git
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
    sharelatex-versioning download-zip --in_file /path/to/config.json --working_dir /path/to/repository
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

If you have any question, please contact [Patrick Stoeckle](mailto:patrick.stoeckle@tum.de)
 



