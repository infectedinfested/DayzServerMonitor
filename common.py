
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
