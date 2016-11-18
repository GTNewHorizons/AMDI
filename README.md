# AMDI
Awesome Minecraft Data Importer

AMDI was created for the purpose of importing player-profiles, stats and grave-data into a MySQL Database, in order to query all sorts of stats (for a community page), and to find grave-data for openblock in a faster way than browsing the filesystem.

Requirements:
- Python 2.7
- MySQL 5.7+ (It needs the JSON Data-type of 5.7)
- The Python packages "pymysql" and "nbt". Install via:
- pip install pymysql
- pip install nbt
