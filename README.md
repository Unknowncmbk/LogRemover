# LogRemover
Python script that removes .log files until filesystem utilization is under x%.

## Introduction to LogRemover
LogRemover is a simple Python script that removes the oldest .log files until the total 
filesystem utilization is under x%. The default utilization is 0.8 (80%).

## Background
One of our network filesystems is filling up! Write a shell script (in your favorite scripting 
language) that can be run daily to search a directory tree and remove all the oldest ".log" files
to bring the total filesystem utilization down to 80%.

## Requirements
This program was written and tested on MacOS 10.9.5, and further tested on various Scientific
Linux 6 workstations.
- Python 2.7.+
- Unix required for os.statvfs(), so no Windows.

## Instructions
Run directly from command line as Python script:
```
python log_remover.py /path/to/dir/
```

Example:
If /path/to/dir/ to clean is within same directory as file:
```
python log_remover.py ./
```

Example:
If /path/to/dir/ is top level:
```
python log_remover.py /
```

Note: Everytime the script is executed, the results are logged to a file called log_remover.log.
```
Mon Apr 13 22:00:05 2015: Usage of 75.3% within limit of 80.0%.
```

## Improvements
The following improvements can be made on this program:
- Allow for user input on system utilization.
- Allow for user input on pattern matching (not just .log files)

## License
A copy of the LogRemover's license can be found [here](https://github.com/Unknowncmbk/LogRemover/blob/master/LICENSE).
