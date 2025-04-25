<!--
Copyright © Patrick Stoeckle 2020 - 2025

Licensed under the Apache License License 2.0

Authors: Patrick Stoeckle, Patrick Stöckle

SPDX-FileCopyrightText: 2020 Patrick Stoeckle

SPDX-License-Identifier: Apache-2.0
-->

# ShareLaTeX-Versioning

**The code in this repository can only pull from ShareLaTeX/Overleaf.**
**For a more sophisticated version, have a look at [python-sharelatex](https://gitlab.inria.fr/sed-rennes/sharelatex/python-sharelatex)**

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
2. Install the package

    ```bash
    pip install sharelatex-versioning
    ```

    Now you should be able to call `sharelatex-versioning` within your shell.

    **Attention**: On macOS, `pip` is usually the installer of the Python2 instance.
    Please use `pip3` or `pip3.x` in this case.

## Repository Setup

1. Open your ShareLaTeX project.
5. In the URL field of your browser, the link of your project should look like this.

    ```bash
   https://sharelatex.tum.de/project/this-is-your-project-id
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
        "sharelatex_url": "https://sharelatex.tum.de/"
    }
    ```

    Replace the placeholders with your values.
11. Store the password in the password manager using [keyring](https://pypi.org/project/keyring/).

   ```bash
   sharelatex-versioning store-password-in-password-manager --user_name "your LRZ ID" --password "your password"
   ```

   Afterward, the password should be in the password manager, e.g., in the Keychain on macOS.
   For deleting the password again, c.f. [here](#store-password-in-password-manager).

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

## Command line usage

```bash
sharelatex-versioning --help
Usage: sharelatex-versioning [OPTIONS] COMMAND [ARGS]...

  :return:

Options:
  --version  Version
  --help     Show this message and exit.

Commands:
  download-zip                    This command downloads your ShareLaTeX...
  store-password-in-password-manager
                                  Stores the password in the password...
```

### Download ZIP

```bash
sharelatex-versioning download-zip --help
Usage: sharelatex-versioning download-zip [OPTIONS]

  This command downloads your ShareLaTeX project as ZIP compressed file.
  Next, the zip folder is extracted into the current directory. All files
  are made readonly as the local repository should not be the place to edit
  the files. If you want, the script can also delete all the files which are
  no longer in your project. Thus, files deleted on the ShareLaTeX instance
  are also deleted locally.

Options:
  -f, --force             If this flag is passed, all the files which are not
                          part of the ShareLaTeX project and not covered by
                          .gitignore or the white_list option, are deleted.

  -i, --in_file TEXT      The path of a JSON file containing the information
                          of the ShareLaTeX project.

  -w, --white_list TEXT   The path of a file containing all the files which
                          are not part of the ShareLaTeX project, but should
                          not be deleted. You can use UNIX patterns.

  -d, --working_dir TEXT  The path of the working dir
  --help                  Show this message and exit.
```

### Store Password In Password Manager

```bash
sharelatex-versioning store-password-in-password-manager --help
Usage: sharelatex-versioning store-password-in-password-manager
           [OPTIONS]

  Stores the password in the password manager.

Options:
  -f, --force           If true, we will overwrite existing passwords.
  -p, --password TEXT   The password for the Overleaf/ShareLaTex instance.
  -u, --user_name TEXT  The username
  --help                Show this message and exit.
```

In case, you want to delete the password again, you can use the [Windows Credential Manager](https://kb.intermedia.net/Article/44527) or [Keychain](https://www.wikihow.com/Delete-Saved-Passwords-from-the-iCloud-Keychain-on-macOS).

#### Store Password In Password Manager: Example

```bash
sharelatex-versioning store-password-in-password-manager --user_name "your LRZ ID" --password "your password"
```

## Contact

If you have any question, please contact [Patrick Stöckle](mailto:patrick.stoeckle@posteo.de).
