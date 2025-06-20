#!/bin/bash

# Database credentials
DB_USER="root"
DB_PASSWORD="root"
DB_NAME="cookify"

SCHEMA_FILE="create_tables.sql"
TEST_SQL_FILE="test-sample.sql"
TEST_OUT_FILE="test-sample.out"

# --- Script Execution ---

echo "Resetting the database using '$SCHEMA_FILE'..."

mysql -u"$DB_USER" -p"$DB_PASS" < "$SCHEMA_FILE"

if [ $? -ne 0 ]; then
    echo "Error: Failed to reset the database. Please check your credentials and the schema file path."
    exit 1
fi

echo "Database reset successfully."
echo "----------------------------------"
echo "Running test queries from '$TEST_SQL_FILE'..."

mysql -u"$DB_USER" -p"$DB_PASS" "$DB_NAME" < "$TEST_SQL_FILE"

if [ $? -ne 0 ]; then
    echo "Error: Failed to run test queries."
    exit 1
fi

echo "Test queries executed. Output saved to '$TEST_OUT_FILE'."
echo ""
echo "--- Test Output ---"
# Use 'cat' to display the content of the output file
cat "$TEST_OUT_FILE"
echo "-------------------"
echo "Script finished."