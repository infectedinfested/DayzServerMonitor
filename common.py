import yaml
import uuid

import asyncio

from communityZBot import post_alert

def strtobool (val):

    if val in ('y', 'yes', 't', 'true', 'True', '1', 1):
        return 'True'
    elif val in ('n', 'no', 'f', 'false', 'False', '0', 0):
        return "False"
    else:
        raise ValueError("invalid truth value %r" % (val,))



def create_ban_file(bannedPersons,insert):
    with open('DayZServerBackup20220728/ban.txt', insert ) as file:
        header = "//Players added to the ban.txt won't be able to connect to this server.\n//Bans can be added/removed while the server is running and will come in effect immediately, kicking the player.\n//-----------------------------------------------------------------------------------------------------\n//To ban a player, add his player ID (44 characters long ID) which can be found in the admin log file (.ADM).\n//-----------------------------------------------------------------------------------------------------\n//For comments use the // prefix. It can be used after an inserted ID, to easily mark it.\n\n//AABBBCCCCDDDDDEEEEDDDDDFFFF //Example of a character ID\n\n"
        if insert == "w":
            file.write(header)
        for person in bannedPersons:
            line = ""
            if person.active != "True":
                line += "//"

            file.write(line + person.steamid + " // " + person.reason + " // Length:" + person.time+ " // Starting from:" + person.startDate + " // "+ person.comment+"\n")
    return 'write successfull'

def compare_files(backup_path, new_path):
    differences = []

    with open(new_path, 'r') as file1, open(backup_path, 'r') as file2:
        # Read all lines from both files
        newLines = file1.readlines()
        backupLines  = file2.readlines()

        # Compare each line of both files
        i = 0
        j = 0
        while i < len(backupLines) and j < len(newLines):
            if backupLines[i] != newLines[j]:
                # Lines are different, check if one line was just skipped
                if backupLines[i+1:] == newLines[j+1:]:
                    # Lines in file1 were just skipped
                    # differences.append(("skip "+ str(i), newLines[j].strip()))
                    i += 1  # Move to the next line in file1
                elif backupLines[i] == newLines[j+1]:
                    # Line was removed from file1
                    differences.append(("Rem "+ str(j), "Line removed"))
                    j += 1  # Move to the next line in file2
                elif backupLines[i+1] == newLines[j]:
                    # Line was added to file1
                    differences.append(("Add "+ str(i), backupLines[i].strip()))
                    i += 1  # Move to the next line in file1
                else:
                    # Lines are different
                    differences.append(("Dif "+ str(i), backupLines[i].strip() + " <<< "+ newLines[j].strip()))
            i += 1
            j += 1

        # Check if there are additional lines in file1 or file2
        while i < len(backupLines):
            differences.append(("Old "+ str(i), backupLines[i].strip()))
            i += 1
        while j < len(newLines):
            differences.append(("New "+ str(j), newLines[j].strip()))

    return differences

def p(path):
    path = path.split(".")
    with open("settings.yaml", 'r') as f:
        settings = yaml.safe_load(f)
    for i in path:
        settings = settings.get(i)
    return settings

def error(err,descr = "",id = ""):
    error = ""
    description = ""
    if isinstance(err, Exception):
        str_err = str(err)
        start_index = str_err.find("(")
        end_index = str_err.rfind(")")
        if not id:
            id = uuid.uuid4()
        error = str(type(err)).split("'")[1]
        description = str_err[start_index + 1:end_index],
    else:
        error = err
        description = descr

    error = {
            "error": error,
            "description": description,
            "identifier": id
        }
    return error

def sendDiscordAlert(channel, message) -> None:
    asyncio.run(post_alert(channel, message))


