# tests data

Static non-Python files used for tests.

Files are compressed on the `testdata.zip` file, which is read from the tests, and the file/s required read in-memory during test execution.

To add or update a file:

1. Extract the zip on this directory (the extracted files should no be git-commited; they're already gitignored).
2. Perform the changes required.
3. Execute the `generate.sh` script, which will create/update the zip file.
