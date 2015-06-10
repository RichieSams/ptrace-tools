# Overview #
The ptrace-tools project aims to provide a simple suite of tools to analyze thread execution within a process. It runs entirely in user-space and does not require any linux kernel modifications. Furthermore it does not require the process to be modified in any way.

ptrace-tools is broken up into 2 parts, the tracing and the analysis. The tracing part is a tool which is run that traces the execution of the threads of a process. The analysis tools analyze the the trace. The tracing tool records the trace to the disk in a file called ptrace.log.

The analysis of the trace file can either be done with a simple command line analyzer or a gui analyzer which enables one to visualize the execution and events of the processes' threads.

## Screen Shots ##
![http://ptrace-tools.googlecode.com/files/ptrace.png](http://ptrace-tools.googlecode.com/files/ptrace.png)

## How to use ##
### Trace a process ###
To trace a process, from the command line type
```
pthread-trace <process to run> <command line arguments to process>
```

After the program has finished running there should be a file called ptrace.log in the directory where you ran the program.
### Analyze a process ###
There are two options to analyze a process, one is a simple commandline tool, the other is a gui which visualizes the thread exection

#### command-line tool ####
```
ptrace-analyze.py <trace file>
```

gui tool
```
ptracegui.py [<trace file>]
```

NOTE:The gui tool does not require there to be a trace file as an argument, as the user can open a trace file from the file menu.

### Examples ###
The code comes with a sample trace called ptrace.log it is in the samples directory.

#### command-line example ####
```
#./ptrace-analyze.py ../samples/ptrace.log

--- process information ---
Process execution time: 5.7260 seconds
Number of threads: 3

---- Thread Stats for Thread ID: 7240 ----
Total run time of thread: 5696425181ns
Average wait time: 14384ns
Max wait time: 108100ns
Thread waited 0 percent of run time
Total thread wait time: 647304ns

---- Thread Stats for Thread ID: 7241 ----
Total run time of thread: 5696853618ns
Average wait time: 2746565ns
Max wait time: 15477518ns
Thread waited 99 percent of run time
Total thread wait time: 5657925714ns
                                                                                                
---- Thread Stats for Thread ID: 7239 ----                                                      
Total run time of thread: 5725987302ns                                                          
Average wait time: 13465ns                                                                      
Max wait time: 130938ns                                                                         
Thread waited 0 percent of run time                                                             
Total thread wait time: 5938092ns
```