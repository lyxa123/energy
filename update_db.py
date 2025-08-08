import sqlite3

# Connect to the database
conn = sqlite3.connect('power_grid.db')
cursor = conn.cursor()

print("Updating database to rename SUPPLIER to POWER_STATION...")

# Update SavedInstances table - change component_type from SUPPLIER to POWER_STATION
cursor.execute('''
    UPDATE SavedInstances 
    SET component_type = 'POWER_STATION' 
    WHERE component_type = 'SUPPLIER'
''')

# Update UserConfigs table - change component_type from SUPPLIER to POWER_STATION
cursor.execute('''
    UPDATE UserConfigs 
    SET component_type = 'POWER_STATION' 
    WHERE component_type = 'SUPPLIER'
''')

# Update ComponentConfigs table - change component_type from SUPPLIER to POWER_STATION
cursor.execute('''
    UPDATE ComponentConfigs 
    SET component_type = 'POWER_STATION' 
    WHERE component_type = 'SUPPLIER'
''')

# Commit the changes
conn.commit()

# Check the results
print("\nUpdated records:")

cursor.execute('SELECT component_type, COUNT(*) FROM SavedInstances GROUP BY component_type')
saved_instances = cursor.fetchall()
print("SavedInstances by type:", saved_instances)

cursor.execute('SELECT component_type, COUNT(*) FROM UserConfigs GROUP BY component_type')
user_configs = cursor.fetchall()
print("UserConfigs by type:", user_configs)

cursor.execute('SELECT component_type, COUNT(*) FROM ComponentConfigs GROUP BY component_type')
component_configs = cursor.fetchall()
print("ComponentConfigs by type:", component_configs)

conn.close()
print("\nDatabase update complete!")
