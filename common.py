import yaml
from datetime import timedelta

def toBool(val):
    if val in ('y', 'yes', 't', 'true', 'True', '1', 1):
        return 'True'
    elif val in ('n', 'no', 'f', 'false', 'False', '0', 0):
        return "False"
    else:
        raise ValueError("invalid truth value %r" % (val,))



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



def get_timeDelta(amount):
    match amount:
        case "1d": return timedelta(days=1)
        case "2d": return timedelta(days=2)
        case "3d": return timedelta(days=3)
        case "1w": return timedelta(weeks=1)
        case "2w": return timedelta(weeks=2)
        case "3w": return timedelta(weeks=3)
        case "1m": return timedelta(days=30)
        case "2m": return timedelta(days=60)
        case "3m": return timedelta(days=90)
        case "6m": return timedelta(days=182)
        case "1y": return timedelta(days=365)
        case _: return timedelta(days=36500)
