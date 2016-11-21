import nbt
import pymysql
from uuid import UUID
from nbt2json import *
import hashlib
import sys
import getopt

connection = ''
g_minecraft_basedir = ''


def get_or_create_playerid(p_player_uuid, p_player_name):
    with connection.cursor() as cur:
        sql = "SELECT * FROM mcuserprofiles WHERE UUID = %s"
        row_count = cur.execute(sql, (p_player_uuid, ))
        if row_count > 0:
            res = cur.fetchone()
            t_player_id = res["ID"]
            if res["LastName"] == "__TMP_NOTSET":
                if p_player_name:
                    cur.execute("UPDATE mcuserprofiles SET LastName = %s WHERE ID = %s", (p_player_name, tPlayerID))
                    connection.commit()

            return t_player_id
        else:
            tPlayerName = p_player_name
            if not p_player_name:
                tPlayerName = "__TMP_NOTSET"

            cur.execute("INSERT INTO mcuserprofiles (UUID, LastName) VALUE (%s, %s)", (p_player_uuid, tPlayerName))
            connection.commit()
            return cur.lastrowid


def validate_uuid(p_uuid):
    try:
        val = UUID(p_uuid, version=4)
    except ValueError:
        return False
    
    return val.hex == p_uuid

# ============================================================================


# Dump all .json stat-files into our DB
def dump_stats_to_sql():
    sql_stats_insert = "INSERT INTO mcstats (playerID, statsJson) VALUES (%s, %s)"
    sql_stats_update = "UPDATE mcstats SET statsJson = %s, crc = %s WHERE ID = %s"
    sql_stats_query = "SELECT ID, crc from mcstats WHERE playerID = %s"

    indir = g_minecraft_base_dir + '/stats/'
    t_counter_new = 0
    t_counter_update = 0
    with connection.cursor() as cur:
        for root, dirs, filenames in os.walk(indir):
            for f in filenames:
                if f.endswith(".json"):
                    json_data = open( indir + f ).read()
                    # Replace all dots
                    json_data = json_data.replace(".", "")
                    json_hash = hashlib.sha256(json_data).hexdigest()
                    tUUID = f[:-5]
                    tPlayerID = get_or_create_playerid(tUUID, "")
                    row_count = cur.execute(sql_stats_query, (tPlayerID,))
                    if row_count > 0:
                        print ("Existing stat-row found, checking CRC")
                        res = cur.fetchone()
                        tCRC = res["crc"]
                        tID = res["ID"]
                        if tCRC != json_hash:
                            print ("CRC mismatch; Stat file has changed. Updating")
                            connection.cursor().execute(sql_stats_update, (json_data, json_hash, tID))
                            t_counter_update += 1
                        else:
                            print ("CRC match; Nothing to do")
                            continue
                    else:
                        print ("No existing stat-row found. Creating new")
                        connection.cursor().execute(sql_stats_insert, (tPlayerID, json_data))
                        connection.commit()
                        t_counter_new += 1

    print("Imported " + str(t_counter_new) + " new Stats and updated " + str(t_counter_update) + " existing ones")


# Dump all player-profiles into our DB
def dump_playerprofile_to_sql():
    sql_profile_insert = "INSERT INTO mcprofiles (playerID, PlayerDat) VALUES (%s, %s)"
    sql_profile_update = "UPDATE mcprofiles SET PlayerDat = %s, crc = %s WHERE ID = %s"
    sql_profile_query = "SELECT ID, crc from mcprofiles WHERE playerID = %s"
    t_counter_new = 0
    t_counter_update = 0

    with connection.cursor() as cur:
        indir = g_minecraft_base_dir + '/playerdata/'
        for root, dirs, filenames in os.walk(indir):
            for f in filenames:
                tFullPath = indir + f
                tUserUUID = f[:-4]
                tCleanUUID = tUserUUID.replace("-", "")
                if validate_uuid(tCleanUUID): # make sure to not parse crap; only grab UUID files
                    tNBTFile = nbt.nbt.NBTFile(tFullPath)
                    tLastKnownName = str(tNBTFile["bukkit"]["lastKnownName"])
                    tPlayerID = get_or_create_playerid(tUserUUID, tLastKnownName)
                    json_data = convert2json(tFullPath)
                    json_hash = hashlib.sha256(json_data).hexdigest()

                    row_count = cur.execute(sql_profile_query, (tPlayerID,))
                    if row_count > 0:
                        print ("Existing playerdat-row found, checking CRC")
                        res = cur.fetchone()
                        tCRC = res["crc"]
                        tID = res["ID"]
                        if tCRC != json_hash:
                            print ("CRC mismatch; playerdat file has changed. Updating")
                            connection.cursor().execute(sql_profile_update, (json_data, json_hash, tID))
                            connection.commit()
                            t_counter_update += 1
                        else:
                            print ("CRC match; Nothing to do")
                            continue
                    else:
                        print ("No existing playerdat-row found. Creating new")
                        connection.cursor().execute(sql_profile_insert, (tPlayerID, json_data))
                        connection.commit()
                        t_counter_new += 1

                    cur.execute(sql_profile_insert, (tPlayerID, json_data))
                    t_counter_new += 1

    print("Imported " + str(t_counter_new) + " new player profiles and updated " + str(t_counter_update) + " existing ones")


# Parse all -grave- files in given dim-directory and dump the info into our DB
def dump_gravedim_to_sql(pDimension):
    tCounter = 0
    sql_grave_query = "SELECT count(ID) from graves WHERE graveFullPath = %s"
    tSQLInsert = "INSERT INTO graves (playerID, graveDim, graveFullPath, gravedata) VALUES (%s, (SELECT ID FROM dimensionref WHERE DimName = %s), %s, %s)"

    indir = ""
    if not pDimension:
        indir = g_minecraft_base_dir + '/data/'
    else:
        indir = g_minecraft_base_dir + pDimension + '/data/'

    with connection.cursor() as cur:
        for root, dirs, filenames in os.walk(indir):
            for f in filenames:
                if "-grave-" in f:
                    tFullPath = indir + f
                    tNBTFile = nbt.nbt.NBTFile(tFullPath, 'r')
                    tPlayerUUID = str(tNBTFile["PlayerUUID"])
                    tPlayerName = str(tNBTFile["PlayerName"])

                    tPlayerSQLID = get_or_create_playerid(tPlayerUUID, tPlayerName)

                    row_count = cur.execute(sql_grave_query, (tFullPath,))
                    if row_count > 0:
                        print("Grave file " + tFullPath + " is already known. Skipping")
                    else:
                        cur.execute(tSQLInsert, (tPlayerSQLID,
                                                 pDimension,
                                                 tFullPath,
                                                 convert2json(tFullPath)))
                    tCounter += 1

    connection.commit()

    print("Imported " + str(tCounter) + " Graves")


# Get the dim-info from SQL that shall be processed and trigger read functions
def iterate_defined_dimensions():
    with connection.cursor() as cur:
        sql = "SELECT DimName FROM dimensionref"
        row_count = cur.execute(sql, ())
        if row_count == 0:
            print ("No Dimensions are defined!")
        else:
            for x in xrange(0, row_count):
                row = cur.fetchone()
                dimName = row["DimName"]
                print("Processing DIM > " + dimName + " <")
                dump_gravedim_to_sql(dimName)


def clean_tables():
    with connection.cursor() as cur:
        cur.execute("TRUNCATE TABLE mcstats")
        connection.commit()
        cur.execute("TRUNCATE TABLE mcprofiles")
        connection.commit()
        cur.execute("TRUNCATE TABLE graves")
        connection.commit()


def print_help():
    print 'amdi.py [-h/-s/-f/] [-i/-ipath] <inputfile> -c <db-server> -d <db-name> -u <db-user> -p <db-password>'
    print 'Args: '
    print ' -h : Show help'
    print ' -s : Run in Sync-Mode. Will resync DB to folder'
    print ' -f : Run in Full-Mode. Will erase DB Data and import from scratch'
    print ' -i : Specify input-folder. This folder MUST CONTAIN playerdata, data and region subfolders!'
    print '      It must also end with a slash; Ex: /opt/minecraft/server/worldname/'
    print ' -c : IP/Hostname of the MySQL Server'
    print ' -d : Database-Name'
    print ' -u : Username for the MySQL connection'
    print ' -p : Password for the MySQL connection'


def setup_db_connection(pServer, pDB, pUser, pPw):
    global connection
    connection = pymysql.connect(host=pServer,
                                 user=pPw,
                                 password=pUser,
                                 db=pDB,
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)


def run_sync_mode():
    dump_playerprofile_to_sql()
    dump_stats_to_sql()
    iterate_defined_dimensions()


def run_full_mode():
    clean_tables()
    run_sync_mode()


def main(argv):
    global g_minecraft_base_dir
    db_server = ''
    db_name = ''
    db_user = ''
    db_pw = ''

    runmode = 0
    totalArgsSet = 0

    try:
        opts, args = getopt.getopt(argv,"hsfi:c:u:p:d:")
    except getopt.GetoptError:
        print_help()
        sys.exit()

    for opt, arg in opts:
        if opt == '-h':
            print_help()
            sys.exit()
        elif opt == "-i":
            g_minecraft_base_dir = arg
            totalArgsSet += 1
        elif opt == "-c":
            db_server = arg
            totalArgsSet += 1
        elif opt == "-d":
            db_name = arg
            totalArgsSet += 1
        elif opt == "-u":
            db_user = arg
            totalArgsSet += 1
        elif opt == "-p":
            db_pw = arg
            totalArgsSet += 1
        elif opt == "-s":
            if runmode != 0:
                print("ERROR: You can not specify -s and -f together!")
                sys.exit(2)
            else:
                runmode = 1
        elif opt in ("-f"):
            if runmode != 0:
                print("ERROR: You can not specify -s and -f together!")
                sys.exit(2)
            else:
                runmode = 2

    if totalArgsSet != 5 or runmode == 0:
        print_help()
        sys.exit(2)
    else:
        setup_db_connection(db_server,db_name,db_user,db_pw)
        if runmode == 1:
            run_sync_mode()
        elif runmode == 2:
            run_full_mode()
        else:
            print("Invalid Runmode")
            sys.exit(2)


if __name__ == "__main__":
    main(sys.argv[1:])
