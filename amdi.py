import nbt
import pymysql
import time
from uuid import UUID
from nbt2json import *

# Define the path of your minecraft server world here
# This folder must contain the "playerdata", "data" and "region" folders!
minecraft_base_dir = "E:/Projekte/Python/MCStatDumper/DreamCraft/"

# Set your sql connection info here
connection = pymysql.connect(host='localhost',
                             user='root',
                             password='root',
                             db='mcdatadump',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

# ========================================================
# End of config
# ========================================================

def get_or_create_playerid(pPlayerUUID, pPlayerName):
    with connection.cursor() as cur:
        sql = "SELECT * FROM mcuserprofiles WHERE UUID = %s"
        row_count = cur.execute(sql, (pPlayerUUID, ))
        if row_count > 0:
            res = cur.fetchone()
            tPlayerID = res["ID"]
            if res["LastName"] == "__TMP_NOTSET":
                if pPlayerName:
                    cur.execute("UPDATE mcuserprofiles SET LastName = %s WHERE ID = %s", (pPlayerName, tPlayerID))
                    connection.commit()

            return tPlayerID
        else:
            tPlayerName = pPlayerName
            if not pPlayerName:
                tPlayerName = "__TMP_NOTSET"

            cur.execute("INSERT INTO mcuserprofiles (UUID, LastName) VALUE (%s, %s)", (pPlayerUUID, tPlayerName))
            connection.commit()
            return cur.lastrowid

def validate_uuid( pUUID ):
    try:
        val = UUID(pUUID, version=4)
    except ValueError:
        return False
    
    return val.hex == pUUID

# ============================================================================

# Dump all .json stat-files into our DB
def dump_stats_to_sql():
    tSQLInsert = "INSERT INTO mcstats (playerID, statsJson) VALUES (%s, %s)"
    indir = minecraft_base_dir + '/stats/'
    tCounter = 0
    for root, dirs, filenames in os.walk(indir):
        for f in filenames:
            if f.endswith(".json"):
                json_data = open( indir + f ).read()
                tUUID = f[:-5]
                tPlayerID = get_or_create_playerid(tUUID, "")
                connection.cursor().execute(tSQLInsert, (tPlayerID, json_data))
                connection.commit()
                tCounter += 1

    print("Imported " + str(tCounter) + " Stats")

# Dump all player-profiles into our DB
def dump_playerprofile_to_sql():
    tCounter = 0
    with connection.cursor() as cur:
        indir = minecraft_base_dir + '/playerdata/'
        for root, dirs, filenames in os.walk(indir):
            for f in filenames:
                tFullPath = indir + f
                tUserUUID = f[:-4]
                tCleanUUID = tUserUUID.replace("-", "")
                if validate_uuid(tCleanUUID): # make sure to not parse crap; only grab UUID files
                    tNBTFile = nbt.nbt.NBTFile(tFullPath)
                    tLastKnownName = str(tNBTFile["bukkit"]["lastKnownName"])
                    tPlayerID = get_or_create_playerid(tUserUUID, tLastKnownName)
                    cur.execute("INSERT INTO mcprofiles (playerID, PlayerDat) VALUES (%s, %s)", (tPlayerID, convert2json(tFullPath)))
                    tCounter += 1

    connection.commit()
    print("Imported " + str(tCounter) + " Player-Profiles")

# Parse all -grave- files in given dim-directory and dump the info into our DB
def dump_gravedim_to_sql(pDimension):
    tCounter = 0
    tSQLInsert = "INSERT INTO graves (playerID, graveDim, graveFullPath, gravedata) VALUES (%s, (SELECT ID FROM dimensionref WHERE DimName = %s), %s, %s)"
    indir = ""
    if not pDimension:
        indir = minecraft_base_dir + '/data/'
    else:
        indir = minecraft_base_dir + pDimension + '/data/'

    with connection.cursor() as cur:
        for root, dirs, filenames in os.walk(indir):
            for f in filenames:
                if "-grave-" in f:
                    tFullPath = indir + f
                    tNBTFile = nbt.nbt.NBTFile(tFullPath, 'r')
                    tPlayerUUID = str(tNBTFile["PlayerUUID"])
                    tPlayerName = str(tNBTFile["PlayerName"])

                    tPlayerSQLID = get_or_create_playerid(tPlayerUUID, tPlayerName)
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


start_time = time.time()
print("==== ================================================================= ====")
print("====       Welcome to A.M.D.I. (Awesome Minecraft Data Importer)       ====")
print("==== ================================================================= ====")
print("  == This script will now import all your stats, profiles and graves   ==")
print("  == into your MySQL Database for later usage. We will truncate any    ==")
print("  == old data before we start, so you won't get old remains in your DB ==")
print("  == Global UUIDs and Names are stored forever, for easier lookup      ==")
print("  == ================================================================= ==")
raw_input("Press any key to start!")
print("== Ok, let's do this. (This may take a while, you can grab a coffee)")
print("== Cleaning Tables...")
single_start_time = time.time()
clean_tables()
print("== ... done. Took %s seconds" % (time.time() - single_start_time))

print("Importing Player-Profiles...")
single_start_time = time.time()
dump_playerprofile_to_sql()
print("== ... done. Took %s seconds" % (time.time() - single_start_time))

print("Importing Player-Stats...")
single_start_time = time.time()
dump_stats_to_sql()
print("== ... done. Took %s seconds" % (time.time() - single_start_time))

print("Importing Player-Graves...")
single_start_time = time.time()
iterate_defined_dimensions()
print("== ... done. Took %s seconds" % (time.time() - single_start_time))

print("=====================================================================")
print(" DataImport complete")
print(" Total execution time: %s" % (time.time() - start_time))
print("=====================================================================")

